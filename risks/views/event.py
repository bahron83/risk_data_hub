import re
from django.conf import settings
from geonode.utils import json_response
from risks.views.base import FeaturesSource
from risks.views.hazard_type import HazardTypeView
from risks.views.data_extraction import DataExtractionView
from risks.models import (Event, RiskAnalysis, AnalysisType, AdministrativeDivision, 
                            AdministrativeDivisionMappings, AdministrativeData,
                            AdministrativeDivisionDataAssociation)

class EventView(FeaturesSource, HazardTypeView):
    def get_events(self, **kwargs):        
        ids = kwargs['evt'].split('__')
        return Event.objects.filter(pk__in=ids)        

    def get_current_adm_level(self, **kwargs):
        return kwargs['lvl']

    def get(self, request, *args, **kwargs):
        locations = self.get_location(**kwargs)
        app = self.get_app()
        if not locations:
            return json_response(errors=['Invalid location code'], status=404)
        loc = locations[-1]

        #hazard_type = self.get_hazard_type(loc, **kwargs)
        try:
            risk_analysis = RiskAnalysis.objects.get(id=kwargs['an'])
        except RiskAnalysis.DoesNotExist:
            return json_response(errors=['Invalid risk analysis'], status=404)

        events = self.get_events(**kwargs)
        if not events:
            return json_response(errors=['Invalid event Id(s)'], status=404)

        adm_level = self.get_current_adm_level(**kwargs)

        #if not hazard_type:
            #return json_response(errors=['Invalid hazard type'], status=404)
        
        wms_events = {
            'style': None,
            'viewparams': self.get_viewparams(adm_level, risk_analysis, events),
            'baseurl': settings.OGC_SERVER['default']['PUBLIC_LOCATION']            
        }

        layer_style = {
            'name': 'monochromatic',
            'title': None,
            'url': 'http://localhost:8080/geoserver/rest/styles/monochromatic.sld'
        }

        layer_events = {
            'layerName': 'geonode:risk_analysis_event_location',
            'layerStyle': layer_style,
            'layerTitle': 'risk_analysis_event_location'
        }  
        
        related_layers_events = [(l.id, l.typename, l.title, ) for l in events.first().related_layers.all()] if events.count() == 1 else []
        
        feat_kwargs = self.url_kwargs_to_query_params(**kwargs)
        features = self.get_features_base('geonode:risk_analysis', None, **feat_kwargs)
        
        values = [[f['properties']['dim1_value'], f['properties']['dim2_value'], f['properties']['value']] for f in features['features']]


        out = {
            'wms': wms_events,
            'layer': layer_events,
            'relatedLayers': related_layers_events,
            'eventValues': values
        }        

        return json_response(out)

    def get_viewparams(self, adm_level, risk_analysis, events):
        event_ids = '__'.join([e.event_id for e in events])
        
        actual_geom_lookup = int(adm_level) > 1
        target_level = int(adm_level) if actual_geom_lookup else int(adm_level) + 1

        adm_codes_list = []         
        for event in events:
            for adm in event.administrative_divisions.all():                
                if(adm.level == target_level):
                    adm_codes_list.append(adm.code)
        adm_codes = "__".join(list(set(adm_codes_list)))        
        return 'adm_codes:{};risk_analysis:{};event_ids:{};actual_geom_lookup:{}'.format(adm_codes, risk_analysis.name, event_ids, actual_geom_lookup)


class EventDetailsView(DataExtractionView):
    def get_risk_analysis(self, **kwargs):
        try:
            return RiskAnalysis.objects.get(id=kwargs['an'])
        except RiskAnalysis.DoesNotExist:
            pass

    def get_risk_analysis_group(self, hazard_type, **kwargs):
        ref_ra = self.get_risk_analysis(**kwargs)        
        analysis_types = AnalysisType.objects.filter(analysis_class=ref_ra.analysis_type.analysis_class)
        return RiskAnalysis.objects.filter(region=ref_ra.region, hazard_type=hazard_type, analysis_type__in=analysis_types)

    def get_event(self, **kwargs):
        try:
            return Event.objects.get(event_id=kwargs['evt'])
        except Event.DoesNotExist:
            pass

    def get_related_ra(self, hazard_type, dym_values, analysis_type, event):        
        #if 'TOTAL' not in [d.upper() for d in dym_values]:
        #    dym_value.append('total')
        ra = RiskAnalysis.objects.filter(
            hazard_type=hazard_type,
            dymensioninfo_associacion__value__upper__in=dym_values,
            analysis_type=analysis_type,
            show_in_event_details=True)
        if event.event_type:
            ra = ra.filter(tags__icontains=event.event_type)
        return ra 

    def removekey(self, d, key):
        r = dict(d)
        del r[key]
        return r   

    def get_related_analysis_type(self, risk_analysis):
        current_atype_name = risk_analysis.analysis_type.name
        if current_atype_name.startswith('e_'):
            try:
                return AnalysisType.objects.get(name=re.sub(r"^e_", r"r_", current_atype_name))  
            except AnalysisType.DoesNotExist:
                return
        elif current_atype_name.startswith('r_'):
            try:
                return AnalysisType.objects.get(name=re.sub(r"^r_", r"e_", current_atype_name))  
            except AnalysisType.DoesNotExist:
                return
    
    def get(self, request, *args, **kwargs):        
        event = self.get_event(**kwargs)
        #location = self.get_location_exact(event.iso2)
        #retrieve data about nuts2 which are not in AdministrativeDivision models 
        nuts3_adm_divs = AdministrativeDivision.objects.filter(level=2, code__in=event.nuts3.split(';'))
        nuts3_ids = nuts3_adm_divs.values_list('id', flat=True)                   
        nuts2_codes = AdministrativeDivisionMappings.objects.filter(child__pk__in=nuts3_ids).order_by('code').values_list('code', flat=True).distinct()
        nuts3_in_nuts2 = list(AdministrativeDivisionMappings.objects.filter(code__in=nuts2_codes).values_list('child__code', flat=True))
        #locations = self.get_location_range(event.nuts3.split(';') + [event.iso2])
        locations = self.get_location_range(nuts3_in_nuts2 + [event.iso2])
        hazard_type = self.get_hazard_type(event.region, locations[0], **kwargs)
        risk_analysis = self.get_risk_analysis(**kwargs)
        an_group = self.get_risk_analysis_group(hazard_type, **kwargs)        
        data = {}  
        overview = {}      
        if an_group and event:
            
            #administrative data
            administrative_data = {}            
            risk_analysis_mapping = {}
            adm_data_entries = AdministrativeData.objects.all()
            location_adm_data = AdministrativeDivisionDataAssociation.objects.filter(adm__in=locations)            
            
            for adm_data_entry in adm_data_entries:                 
                ra_match = RiskAnalysis.objects.filter(hazard_type=hazard_type, region=risk_analysis.region, analysis_type__name__contains=adm_data_entry.indicator_type).first()
                if ra_match:
                    risk_analysis_mapping[adm_data_entry.name] = ra_match.analysis_type.name
                administrative_data[adm_data_entry.name] = {
                        'unitOfMeasure': adm_data_entry.unit_of_measure,
                        'values': {}
                }
                for location in locations:
                    data_exact = location_adm_data.filter(data=adm_data_entry, adm=location).order_by('-dimension').first()                                        
                    if data_exact:                           
                        administrative_data[adm_data_entry.name]['values'][data_exact.adm.code] = {
                            'value': data_exact.value,
                            'dimension': data_exact.dimension
                        }

            overview = {                
                'event': event.get_event_plain(),
                'administrativeData': administrative_data,
                'riskAnalysisMapping': risk_analysis_mapping,
                'threshold': 1.5
            }

            for an_event in an_group:                
                adjusted_kwargs = {
                    'loc': event.iso2,                    
                    'ht': kwargs['ht'],
                    'evt': kwargs['evt'],
                    'an': an_event.name
                }            
                feat_kwargs = self.url_kwargs_to_query_params(**adjusted_kwargs)
                features = self.get_features_base('geonode:risk_analysis_event_details', None, **feat_kwargs)                
                dymlist = an_event.dymension_infos.all().distinct()
                dimension = dymlist.filter(riskanalysis_associacion__axis=self.AXIS_X).distinct().get()                
                an_event_values = self.reformat_features(an_event, dimension, dymlist, features['features'], True)  
                data['{}'.format(an_event.analysis_type.name)] = an_event_values
                data['{}'.format(an_event.analysis_type.name)]['riskAnalysis'] = an_event.get_risk_details()

                dym_values = [v[0] for v in an_event_values['values']]
                
                #for every analysis bound to current event, find matching risk analysis (based on analysis type)
                matching_ra = self.get_related_ra(hazard_type, dym_values, self.get_related_analysis_type(an_event), event)                                        
                
                #for every match, retrieve sum of values of administrative divisions affected
                for an_risk in matching_ra:
                    data['{}'.format(an_event.analysis_type.name)]['relatedRiskAnalysis'] = an_risk.get_risk_details()
                    adjusted_kwargs['an'] = an_risk.name
                    adjusted_kwargs['loc'] = event.nuts3.replace(';', '__')
                    feat_kwargs = self.url_kwargs_to_query_params(**self.removekey(adjusted_kwargs, 'evt'))
                    features = self.get_features_base('geonode:risk_analysis_grouped_values', None, **feat_kwargs)

                    dymlist = an_risk.dymension_infos.all().distinct()
                    if kwargs.get('dym'):
                        dimension = dymlist.get(id=kwargs['dym'])
                    else:
                        dimension = dymlist.filter(riskanalysis_associacion__axis=self.AXIS_X).distinct().get()                    

                    an_risk_values = self.reformat_features(an_risk, dimension, dymlist, features['features'], True)                

                    merged_values = an_event_values['values'] + an_risk_values['values']
                    data['{}'.format(an_event.analysis_type.name)]['values'] = merged_values # [[str(item).capitalize() for item in row] for row in merged_values]
                   
        return json_response({ 'data': data, 'overview': overview })