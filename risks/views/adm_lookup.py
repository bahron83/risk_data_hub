from django.views.generic import View
from geonode.utils import json_response
from risks.views.base import ContextAware, LocationSource


class AdmLookupView(ContextAware, LocationSource, View):        
    def get(self, request, *args, **kwargs):
        lookup_data = []
        
        loc_chains = self.location_lookup(**kwargs)
        if loc_chains:                        
            for loc_chain in loc_chains:
                current_loc = loc_chain[-1] 
                country = next((x for x in loc_chain if x.level == 1), None)    
                current_chain_data = {
                    'admCode': current_loc.code,
                    'admName': current_loc.name,
                    'level': current_loc.level,
                    'country': country.code if country is not None else '',
                    'countryName': country.name if country is not None else ''
                }
                lookup_data.append(current_chain_data)
        else:
            lookup_data.append({})
        
        return json_response(lookup_data) 