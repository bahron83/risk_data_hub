from django.views.generic import View
from geonode.utils import json_response
from risks.views.base import ContextAware, LocationSource
from risks.models import HazardType, AnalysisClass


class HazardTypeView(ContextAware, LocationSource, View):    

    def get_hazard_type(self, region, location, **kwargs):
        app = self.get_app()
        try:
            return HazardType.objects.get(mnemonic=kwargs['ht'], app=app).set_region(region).set_location(location)
        except (KeyError, HazardType.DoesNotExist,):
            return

    def get_analysis_type(self, region, location, hazard_type, **kwargs):
        atypes = hazard_type.get_analysis_types()
        aclasses = AnalysisClass.objects.all()
        aclass_risk = aclasses.get(name='risk')
        aclass_event = aclasses.get(name='event')
        if not atypes.exists():
            return None, None, None, None
        
        first_atype = atypes.filter(analysis_class=aclass_risk).first()
        if first_atype is not None:
            first_atype = first_atype.set_region(region).set_location(location).set_hazard_type(hazard_type)
        first_atype_e = atypes.filter(analysis_class=aclass_event).first()
        if first_atype_e is not None:
            first_atype_e = first_atype_e.set_region(region).set_location(location).set_hazard_type(hazard_type)
        if not kwargs.get('at'):
            atype_r = first_atype
            atype_e = first_atype_e
            aclass = None
        else:
            atype = atypes.filter(name=kwargs['at']).first()
            if atype is None:
                return None, None, atypes, None
            else:
                atype = atype.set_region(region).set_location(location).set_hazard_type(hazard_type)            
                atype_r = atype if atype.analysis_class == aclass_risk else first_atype
                atype_e = atype if atype.analysis_class == aclass_event else first_atype_e
                aclass = atype.analysis_class
        return atype_r, atype_e, atypes, aclass,

    def get(self, request, *args, **kwargs):
        reg = self.get_region(**kwargs)
        locations = self.get_location(**kwargs)
        if not locations:
            return json_response(errors=['Invalid location code'], status=404)
        loc = locations[-1]
        app = self.get_app()
        hazard_types = HazardType.objects.filter(app=app)

        hazard_type = self.get_hazard_type(reg, loc, **kwargs)

        if not hazard_type:
            return json_response(errors=['Invalid hazard type'], status=404)

        (atype_r, atype_e, atypes, aclass,) = self.get_analysis_type(reg, loc, hazard_type, **kwargs)
                
        if not atype_r and not atype_e:
            return json_response(errors=['No analysis type available for location/hazard type'], status=404)        

        out = {
            'navItems': [location.set_app(app).set_region(reg).export() for location in locations],
            'overview': [ht.set_region(reg).set_location(loc).export() for ht in hazard_types],
            'context': self.get_context_url(**kwargs),
            'furtherResources': self.get_further_resources(**kwargs),
            'hazardType': hazard_type.get_hazard_details(),            
            'analysisType': atype_r.get_analysis_details() if atype_r else {},
            'analysisTypeE': atype_e.get_analysis_details() if atype_e else {}
        }

        return json_response(out)