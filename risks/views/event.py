import re
import json
import copy
from dateutil.parser import parse as parse_date
from django.conf import settings
from django.db.models import Sum, Count, F, IntegerField, FloatField, Value
from django.db.models.functions import Cast
from django.contrib.postgres.aggregates import ArrayAgg
from geonode.utils import json_response
from risks.views.base import FeaturesSource
from risks.views.auth import UserAuth
from risks.views.hazard_type import HazardTypeView
from risks.views.data_extraction import DataExtractionView
from risks.models import (Event, DamageAssessment, DamageAssessmentEntry, AnalysisType, AdministrativeDivision, 
                            AdministrativeData, AdministrativeDataValue, DataProviderMappings)
from risks.models.location import levels
from risks.helpers.event import EventHelper
from risks.overrides.postgres_jsonb import KeyTextTransform, KeyTransform


EUSF_GDP_THRESHOLD = 0.015
EUSF_INDICATOR = 'GDP'

class EventView(FeaturesSource, HazardTypeView):
    def get_events(self, **kwargs):        
        ids = kwargs['evt'].split('__')
        return Event.objects.filter(pk__in=ids)            

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if not 'an' in data:
            return json_response(errors=['No analysis specified in the request'], status=400)
        if not 'evt' in data:
            return json_response(errors=['No events specified in the request'], status=400)
        if not 'lvl' in data:
            return json_response(errors=['No administrative unit type specified in the request'], status=400)

        try:
            da = DamageAssessment.objects.get(pk=data['an'])
        except DamageAssessment.DoesNotExist:
            return json_response(errors=['Invalid analysis specified in the request'], status=404)
        region = da.region

        # Check user permissions
        user_auth = UserAuth()
        available_datasets, dataset_rule_association = user_auth.resolve_available_datasets(request, region)        
        if da not in available_datasets:
            return json_response(errors=['Data not available for current user'], status=403)

        # Apply visibility rules
        values_after_visibility_rules = user_auth.filter_dataset_values(da, dataset_rule_association)

        current_adm_level = int(data['lvl'])

        events = Event.objects.filter(pk__in=data['evt'])
        related_layers_events = [(l.id, l.typename, l.title, ) for l in events.first().related_layers.all()] if events.count() == 1 else []

        event_entries = values_after_visibility_rules.filter(            
            entry__administrative_division__level__gte=current_adm_level,
            entry__event__id__in=data['evt']
        )

        '''event_entries_lite = event_entries \
            .annotate(
                code=KeyTextTransform('code', KeyTransform('administrative_division', 'entry')),
                level=Cast(KeyTextTransform('level', KeyTransform('administrative_division', 'entry')), IntegerField()),
                geometry=KeyTextTransform('geometry', 'entry'),
                event_id=Cast(KeyTextTransform('id', KeyTransform('event', 'entry')), IntegerField())
            ) \
            .values('code', 'level', 'geometry', 'event_id')'''

        event_locations_count = event_entries \
            .annotate(
                code=KeyTextTransform('code', KeyTransform('administrative_division', 'entry')),
                level=Cast(KeyTextTransform('level', KeyTransform('administrative_division', 'entry')), IntegerField())                
            ) \
            .values('code', 'level') \
            .annotate(occurrences=Count('code'))
        
        event_locations = {}        
        for e in event_locations_count:
            #e['skip'] = False if e['level'] > current_adm_level else True
            event_locations[e['code']] = e
            #if e['level'] > current_adm_level + 1:
            loc = AdministrativeDivision.objects.get(code=e['code'])
            for p in loc.get_parents_chain():
                #if p.level == current_adm_level + 1:
                if p.code in event_locations:
                    event_locations[p.code]['occurrences'] += 1
                else:
                    event_locations[p.code] = {'code': p.code, 'level': p.level, 'occurrences': e['occurrences']}
            #else:
            #   event_locations[e['code']] = e

        out = {
            'eventLocations': event_locations,
            'eventData': list(event_entries.values('entry')),
            'relatedLayers': related_layers_events
        }
        return json_response(out)        

class EventDetailsView(DataExtractionView):
    def get_damage_assessment(self, **kwargs):
        try:
            return DamageAssessment.objects.get(pk=kwargs['an'])
        except DamageAssessment.DoesNotExist:
            pass

    def get_damage_assessment_group(self, damage_assessment):                
        return DamageAssessment.objects.filter(
            region=damage_assessment.region,
            hazard=damage_assessment.hazard,
            scope=damage_assessment.scope)

    def get_event(self, **kwargs):
        try:
            return Event.objects.get(pk=kwargs['evt'])
        except Event.DoesNotExist:
            pass

    def get_related_ra(self, hazard_type, dim1, analysis_type, event):                
        ra = DamageAssessment.objects.filter(
            region=event.region,
            hazard=hazard_type,
            tags__icontains=dim1,
            analysis_type=analysis_type)
        if event.details and 'event_type' in event.details:
            event_type = event.details['event_type']
            if event_type:
                ra = ra.filter(tags__icontains=event_type)
        return ra 

    def removekey(self, d, key):
        r = dict(d)
        del r[key]
        return r   

    def get_related_analysis_type(self, damage_assessment):
        current_atype_name = damage_assessment.analysis_type.name
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
        if not event:
            return json_response(errors=['Invalid Event ID'], status=404)
        eh = EventHelper()

        # Check user permissions
        user_auth = UserAuth()
        available_datasets, dataset_rule_association = user_auth.resolve_available_datasets(request, event.region)

        if not available_datasets.exists():
            return json_response(errors=['Data not available for current user'], status=403)

        # Check if event is published by one of available datasets
        event_entries = DamageAssessmentEntry.objects.filter(
            phenomenon__isnull=False,
            damage_assessment__pk__in=available_datasets.values_list('pk', flat=True),
            entry__event__id=event.id
        )
        if not event_entries.exists():
            return json_response(errors=['Data not available for current user'], status=403)

        # Default data sources
        ordered_data_sources = DataProviderMappings.objects.filter(hazard=event.hazard_type).order_by('order')

        #retrieve data about nuts2 which are not in AdministrativeDivision models 
        '''nuts3_adm_divs = AdministrativeDivision.objects.filter(level=2, code__in=event.nuts3.split(';'))
        nuts3_ids = nuts3_adm_divs.values_list('id', flat=True)                   
        nuts2_codes = AdministrativeDivisionMappings.objects.filter(child__pk__in=nuts3_ids).order_by('code').values_list('code', flat=True).distinct()
        nuts3_in_nuts2 = list(AdministrativeDivisionMappings.objects.filter(code__in=nuts2_codes).values_list('child__code', flat=True))        
        locations = self.get_location_range(nuts3_in_nuts2 + [event.iso2])'''
        locations = list(set([p.administrative_division for p in event.phenomena.all()]))
        extended_locations = copy.deepcopy(locations) 
        for l in locations:
            extended_locations += l.get_parents_chain()
        extended_locations = set(extended_locations)

        hazard_type = self.get_hazard_type(event.region, locations[0], **kwargs)
        damage_assessment = self.get_damage_assessment(**kwargs)
        da_group = self.get_damage_assessment_group(damage_assessment)        
        data = {}  
        overview = {}      
        if da_group:
            
            #administrative data
            administrative_data = {}            
            damage_assessment_mapping = {}
            adm_data_entries = AdministrativeData.objects.all()
            location_adm_data = AdministrativeDataValue.objects.filter(adm__in=extended_locations)                                                            
            gdp_nuts2_affected = 0
            
            for adm_data_entry in adm_data_entries:                
                da_match = DamageAssessment.objects.filter(hazard=hazard_type, region=damage_assessment.region, analysis_type__name__contains=adm_data_entry.indicator_type).first()
                if da_match:
                    damage_assessment_mapping[adm_data_entry.name] = da_match.analysis_type.name
                administrative_data[adm_data_entry.name] = {
                        'unitOfMeasure': adm_data_entry.unit_of_measure,
                        'values': {},
                        'sum': {},
                        'ratios': {}
                }

                value_sum_country = 0
                value_sum_nuts2 = 0
                value_sum_nuts3 = 0
                value_sum_city = 0
                for location in extended_locations:
                    data_exact = location_adm_data.filter(data=adm_data_entry, adm=location).order_by('-dimension').first()
                    if data_exact:                           
                        administrative_data[adm_data_entry.name]['values'][data_exact.adm.code] = {
                            'value': float(data_exact.value),
                            'dimension': data_exact.dimension
                        }

                        if location.level == 1:
                            value_sum_country = float(data_exact.value)
                        
                        if location.level == 2:
                            value_sum_nuts2 += float(data_exact.value)
                            if adm_data_entry.name == EUSF_INDICATOR:
                                gdp_nuts2_affected += float(data_exact.value)

                        if location.level == 3:
                            value_sum_nuts3 += float(data_exact.value)     

                administrative_data[adm_data_entry.name]['sum']['country'] = value_sum_country
                administrative_data[adm_data_entry.name]['sum']['nuts2'] = value_sum_nuts2
                administrative_data[adm_data_entry.name]['sum']['nuts3'] = value_sum_nuts3

            overview = {                
                'event': event.custom_export(),
                'administrativeData': administrative_data,
                'damageAssessmentMapping': damage_assessment_mapping,
                'isEligibleForEUSF': {},
                'threshold': EUSF_GDP_THRESHOLD * 100
            }
            
            for da_event in da_group:
                event_entries_da = event_entries.filter(damage_assessment=da_event)                
                entry = eh.prepare_event_entries(event_entries_da).first()
                if entry:
                    dim1 = entry['dim1']['value']
                    dim2 = entry['dim2']['value']
                    damage_type_values = [dim1, dim2]

                    analysis_type_name = da_event.analysis_type.name
                    data[analysis_type_name] = {}
                    data[analysis_type_name]['dimensions'] = damage_type_values
                    data[analysis_type_name]['eventAnalysis'] = da_event.get_risk_details()
                    data[analysis_type_name]['values'] = entry

                    values_raw = entry['values'][0]
                    data_sources = {}
                    for row in values_raw:                        
                        if row['data_source'] not in data_sources:
                            data_sources[row['data_source']] = row
                        else:
                            current_data_source = data_sources[row['data_source']]
                            is_value_more_recent = parse_date(row['insert_date']) > parse_date(current_data_source['insert_date'])
                            if is_value_more_recent:
                                data_sources[row['data_source']] = row

                    #set event ratios to administrative units
                    adm_data_name = damage_assessment_mapping.keys()[damage_assessment_mapping.values().index(analysis_type_name)]
                    for adm_unit in ['country', 'nuts2', 'nuts3']:                    
                        value_sum = float(overview['administrativeData'][adm_data_name]['sum'][adm_unit])
                        
                        overview['administrativeData'][adm_data_name]['ratios'][adm_unit] = {}
                        for key,val in data_sources.iteritems():
                            value = float(val['value_event'])
                            overview['administrativeData'][adm_data_name]['ratios'][adm_unit][key] = value / value_sum if value_sum > 0 else None
                            #check eligibility for EUSF                
                            if 'economic' in analysis_type_name.lower():                                            
                                overview['isEligibleForEUSF'][key] = value >= gdp_nuts2_affected * EUSF_GDP_THRESHOLD                    
                    
                    #for every analysis bound to current event, find matching risk analysis (based on analysis type)
                    matching_ra = self.get_related_ra(hazard_type, dim1, self.get_related_analysis_type(da_event), event)                                        
                    
                    data[analysis_type_name]['relatedRiskAnalysis'] = []
                    #for every match, retrieve sum of values of administrative divisions affected                
                    for an_risk in matching_ra: 
                        # for scope RISK, there is a single value per row, hence the key 'value' exists in entry                                       
                        an_risk_values = DamageAssessmentEntry.objects \
                            .filter(                                
                                damage_assessment=an_risk,
                                entry__administrative_division__code__in=[l.code for l in locations]
                            ) \
                            .annotate(
                                dim1=KeyTextTransform('value', KeyTransform('dim1', 'entry')),
                                dim2=Cast(KeyTextTransform('value', KeyTransform('dim2', 'entry')), IntegerField())
                            ) \
                            .order_by('dim1', 'dim2') \
                            .values('dim1', 'dim2') \
                            .annotate(value=Sum(Cast(KeyTextTransform('value', 'entry'), FloatField())))

                        data[analysis_type_name]['relatedRiskAnalysis'].append({
                            'riskAnalysis': an_risk.get_risk_details(),
                            'values': list(an_risk_values)
                        })
                   
        return json_response({ 
            'data': data,
            'dataSources': [ds.data_provider.name for ds in ordered_data_sources],
            'overview': overview
        })