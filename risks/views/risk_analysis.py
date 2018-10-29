from django.views.generic import View
from geonode.utils import json_response
from risks.views.base import ContextAware, LocationSource
from risks.models import RiskAnalysis, Region, HazardType, AnalysisClass, AnalysisType

class RiskAnalysisView(ContextAware, LocationSource, View):
    def prepare_data(self, resultset, region, location, rtype = 'risk_analysis'):
        analysisData = []
        for r in resultset:            
            if(rtype == 'risk_analysis'):
                reg=region.name
                loc = location.code
                ht = r.hazard_type.mnemonic
                at = r.analysis_type.name
                an = r.id
                analysisData.append({
                    'riskAnalysis': r.set_region(region).set_location(location).set_hazard_type(r.hazard_type).set_analysis_type(r.analysis_type).export(),
                    'context': {'ht': ht, 'at': at, 'an': r.id, 'reg': reg, 'loc': loc},
                    'analysisType': r.analysis_type.export(r.analysis_type.EXPORT_FIELDS_BASIC),
                    'hazardType': r.hazard_type.set_region(region).set_location(location).export(),
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
        analysis_class = None
        analysis_type = None
        cleaned_args = self.clean_args(**kwargs)
        loc_chain = self.get_location(**kwargs)
        if not loc_chain:
            return json_response(errors=['Invalid location code'], status=404)        
        try:
            region = Region.objects.get(name=kwargs['reg']) 
        except Region.DoesNotExist:
            return json_response(errors=['Invalid region'], status=404)
        loc = loc_chain[-1] 

        if cleaned_args['ht']:
            try:       
                hazard_type = HazardType.objects.get(mnemonic=kwargs['ht'])
            except HazardType.DoesNotExist:
                return json_response(errors=['Invalid hazard type'], status=404)
        if cleaned_args['ac']:
            try:       
                analysis_class = AnalysisClass.objects.get(name=kwargs['ac'])
            except AnalysisClass.DoesNotExist:
                return json_response(errors=['Invalid analysis class'], status=404)            
        if cleaned_args['at']:
            try:       
                analysis_type = AnalysisType.objects.get(name=kwargs['at'])
            except AnalysisType.DoesNotExist:
                return json_response(errors=['Invalid analysis type'], status=404)                                                    

        while loc is not None:
            ra_matches = RiskAnalysis.objects.filter(region=region, administrative_divisions=loc)                           
            if ra_matches:
                if hazard_type:
                    ra_matches = ra_matches.filter(hazard_type=hazard_type)
                if analysis_class:
                    ra_matches = ra_matches.filter(analysis_type__analysis_class=analysis_class)
                if analysis_type:
                    ra_matches = ra_matches.filter(analysis_type=analysis_type)                
                ra_matches = ra_matches.exclude(pk__in=ra_ids) 
                ra_ids += list(ra_matches.values_list('pk', flat=True))
                lookup_data += self.prepare_data(ra_matches, region, loc)                
            loc = loc.parent                                           
        
        return json_response(lookup_data) if lookup_data else json_response(errors=['No data found'], status=204)