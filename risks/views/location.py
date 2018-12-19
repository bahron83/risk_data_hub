from django.views.generic import View
from geonode.utils import json_response
from risks.views.base import ContextAware, LocationSource
from risks.models import Hazard, AnalysisType, scopes

class LocationView(ContextAware, LocationSource, View):

    def get(self, request, *args, **kwargs):
        reg = self.get_region(**kwargs)
        locations = self.get_location(**kwargs)
        if not locations:
            return json_response(errors=['Invalid location code'], status=404)
        loc = locations[-1]        
        app = self.get_app()
        hazard_types = Hazard.objects.filter(app=app)        
        analysis_types = AnalysisType.objects.filter(app=app)
        overview = {
            'hazardType': [ht.set_region(reg).set_location(loc).export() for ht in hazard_types],            
            'analysisType': [at.export(at.EXPORT_FIELDS_BASIC) for at in analysis_types],
            'scope': [s[0] for s in scopes]
        }

        location_data = {'navItems': [location.set_app(app).set_region(reg).export() for location in locations],
                         'context': self.get_context_url(**kwargs),
                         'furtherResources': self.get_further_resources(**kwargs),
                         #'overview': [ht.set_region(reg).set_location(loc).export() for ht in hazard_types],
                         'overview': overview}

        return json_response(location_data)