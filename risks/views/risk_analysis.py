from django.views.generic import View
from geonode.utils import json_response
from risks.views import UserAuth
from risks.views.base import ContextAware, LocationSource
from risks.models import DamageAssessment, Region, Hazard, AnalysisType

class RiskAnalysisView(ContextAware, LocationSource, View):
    def prepare_data(self, resultset, region, location, rtype = 'risk_analysis'):
        analysisData = []
        for r in resultset:            
            if(rtype == 'risk_analysis'):
                reg=region.name
                loc = location.code
                ht = r.hazard.mnemonic
                at = r.analysis_type.name
                an = r.id
                analysisData.append({
                    'riskAnalysis': r.set_region(region).set_location(location).set_hazard_type(r.hazard).set_analysis_type(r.analysis_type).export(),
                    'context': {'ht': ht, 'at': at, 'an': r.id, 'reg': reg, 'loc': loc},
                    'analysisType': r.analysis_type.export(r.analysis_type.EXPORT_FIELDS_BASIC),
                    'hazardType': r.hazard.set_region(region).set_location(location).export(),
                    'location': location.set_region(region).export(),                    
                    'apiUrl': '/risks/data_extraction/reg/{}/loc/{}/ht/{}/at/{}/an/{}/'.format(reg, loc, ht, at, an)
                })
        return analysisData

    def clean_args(self, **kwargs):
        cleaned_args = {}
        for key, value in kwargs.iteritems():    
            cleaned_args[key] = value if value != 'null' else None
        return cleaned_args
    
    def get(self, request, *args, **kwargs):
        lookup_data = []        
        ra_ids = []
        hazard_type = None
        scope = None
        analysis_type = None
        cleaned_args = self.clean_args(**kwargs)
        loc_chain = self.get_location(**kwargs)
        user_auth = UserAuth()
        if not loc_chain:
            return json_response(errors=['Invalid location code'], status=404)        
        try:
            region = Region.objects.get(name=kwargs['reg']) 
        except Region.DoesNotExist:
            return json_response(errors=['Invalid region'], status=404)
        loc = loc_chain[-1] 

        if cleaned_args['ht']:
            try:       
                hazard_type = Hazard.objects.get(mnemonic=kwargs['ht'])
            except Hazard.DoesNotExist:
                return json_response(errors=['Invalid hazard type'], status=404)
        if cleaned_args['ac']:
            try:       
                scope = AnalysisType.objects.get(scope=kwargs['ac'])
            except AnalysisType.DoesNotExist:
                return json_response(errors=['Invalid scope'], status=404)            
        if cleaned_args['at']:
            analysis_type = AnalysisType.objects.filter(title=kwargs['at'])

        available_datasets, dataset_rule_association = user_auth.resolve_available_datasets(request, region)
        if available_datasets:
            while loc is not None:
                ra_matches = available_datasets.filter(administrative_divisions=loc)     
                # example with damage assessment which contains all values as JSONField
                # location_matches = Location.objects.filter(location_type='damage', administrative_division=loc).values_list('id', flat=True)
                # available_datasets.filter(values__location__in=location_matches)  
                # alternative: values contain location_geom and adm_division_id
                # ra_matches = available_datasets.filter(values__adm_division=loc)                      
                if ra_matches:
                    if hazard_type:
                        ra_matches = ra_matches.filter(hazard=hazard_type)
                    if scope:
                        ra_matches = ra_matches.filter(analysis_type__scope=scope)
                    if analysis_type:
                        at_ids = analysis_type.values_list('pk', flat=True)
                        ra_matches = ra_matches.filter(analysis_type__in=at_ids)                
                    ra_matches = ra_matches.exclude(pk__in=ra_ids) 
                    ra_ids += list(ra_matches.values_list('pk', flat=True))
                    lookup_data += self.prepare_data(ra_matches, region, loc)                
                loc = loc.parent                                           
        out = {
            'lookupData': lookup_data#,
            #'datasetRuleAssociation': dataset_rule_association
        }
        return json_response(lookup_data) if lookup_data else json_response(errors=['No data found'], status=204)