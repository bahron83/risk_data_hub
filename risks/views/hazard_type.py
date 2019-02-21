from django.views.generic import View
from geonode.utils import json_response
from risks.views.base import ContextAware, LocationSource
from risks.models.hazard_type import Hazard
from risks.models.analysis_type import AnalysisType
from risks.models.risk_analysis import scopes


class HazardTypeView(ContextAware, LocationSource, View):    

    def get_hazard_type(self, region, location, **kwargs):
        app = self.get_app()
        try:
            return Hazard.objects.get(mnemonic=kwargs['ht'], app=app).set_region(region).set_location(location)
        except (KeyError, Hazard.DoesNotExist,):
            return

    def get_analysis_type(self, region, location, hazard_type, **kwargs):
        atypes = hazard_type.get_analysis_types()        
        if atypes.exists():            
            if 'at' in kwargs:
                atype = atypes.filter(name=kwargs['at']).first()
                if atype:
                    return atype.set_region(region).set_location(location).set_hazard_type(hazard_type)
            else:
                return atypes.first().set_region(region).set_location(location).set_hazard_type(hazard_type)
        
        '''if not atypes.exists():
            return None, None, None, None
        
        first_atype = atypes.filter(scope='risk').first()
        if first_atype is not None:
            first_atype = first_atype.set_region(region).set_location(location).set_hazard_type(hazard_type)
        first_atype_e = atypes.filter(scope='event').first()
        if first_atype_e is not None:
            first_atype_e = first_atype_e.set_region(region).set_location(location).set_hazard_type(hazard_type)
        if not kwargs.get('at'):
            atype_r = first_atype
            atype_e = first_atype_e   
            scope = None         
        else:
            atype = atypes.filter(name=kwargs['at']).first()
            if atype is None:
                return None, None, atypes, None
            else:
                atype = atype.set_region(region).set_location(location).set_hazard_type(hazard_type)            
                atype_r = atype if atype.scope == 'risk' else first_atype
                atype_e = atype if atype.scope == 'event' else first_atype_e
                scope = atype.scope
        return atype_r, atype_e, atypes, scope,'''

    def get(self, request, *args, **kwargs):
        reg = self.get_region(**kwargs)
        locations = self.get_location(**kwargs)
        if not locations:
            return json_response(errors=['Invalid location code'], status=404)
        loc = locations[-1]
        app = self.get_app()
        hazard_types = Hazard.objects.filter(app=app)        
        analysis_types = AnalysisType.objects.filter(app=app)

        hazard_type = self.get_hazard_type(reg, loc, **kwargs)

        if not hazard_type:
            return json_response(errors=['Invalid hazard type'], status=404)

        atype = self.get_analysis_type(reg, loc, hazard_type, **kwargs)
                
        if not atype:
            return json_response(errors=['No analysis type available for location/hazard type'], status=404)        

        overview = {
            'hazardType': [ht.set_region(reg).set_location(loc).export() for ht in hazard_types],
            'analysisClass': list(scopes),
            'analysisType': [at.export(at.EXPORT_FIELDS_BASIC) for at in analysis_types]
        }

        out = {
            'navItems': [location.set_app(app).set_region(reg).export() for location in locations],
            #'overview': [ht.set_region(reg).set_location(loc).export() for ht in hazard_types],
            'overview': overview,
            'context': self.get_context_url(**kwargs),
            'furtherResources': self.get_further_resources(**kwargs),
            'hazardType': hazard_type.get_hazard_details(),            
            'analysisType': atype.get_analysis_details() if atype else {}            
        }

        return json_response(out)
