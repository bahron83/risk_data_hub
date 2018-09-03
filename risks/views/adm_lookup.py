from django.views.generic import View
from geonode.utils import json_response
from risks.views.base import ContextAware, LocationSource
from risks.models import RiskAnalysis

class AdmLookupView(ContextAware, LocationSource, View):
    def prepare_data(self, resultset, location, rtype = 'risk_analysis'):
        analysisData = []
        for r in resultset:            
            if(rtype == 'risk_analysis'):
                loc = location.code
                ht = r.hazard_type.mnemonic
                at = r.analysis_type.name
                an = r.id
                analysisData.append({
                    'riskAnalysis': {'id': r.id, 'name': r.name},
                    'analysisType': at,
                    'hazardType': ht,
                    'admCode': loc,
                    'admName': location.name,
                    'apiUrl': '/risks/data_extraction/loc/{}/ht/{}/at/{}/an/{}/'.format(loc, ht, at, an)
                })
        return analysisData
    
    def get(self, request, *args, **kwargs):
        lookup_data = []
        if 'detail' in kwargs:
            loc_chain = self.get_location(**kwargs)
            if not loc_chain:
                return json_response(errors=['Invalid location code'], status=404)
            
            loc = loc_chain[-1]
            lookup_data = []
            ra_ids = []
            while loc is not None:
                ra_matches = RiskAnalysis.objects.filter(administrative_divisions=loc).exclude(pk__in=ra_ids)                
                if ra_matches:
                    ra_ids += list(ra_matches.values_list('pk', flat=True))
                    lookup_data += self.prepare_data(ra_matches, loc)                
                loc = loc.parent                       
            
        else:
            loc_chains = self.location_lookup(**kwargs)
            if not loc_chains:
                return json_response(errors=['Invalid location code'], status=404)
                        
            for loc_chain in loc_chains:
                current_loc = loc_chain[-1] 
                country = next((x for x in loc_chain if x.level == 1), None)    
                current_chain_data = {
                    'admCode': current_loc.code,
                    'admName': current_loc.name,
                    'country': country.code if country is not None else ''
                }
                lookup_data.append(current_chain_data)
        
        return json_response(lookup_data) 