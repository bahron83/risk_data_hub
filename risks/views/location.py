from django.views.generic import View
from geonode.utils import json_response
from risks.views.base import ContextAware, LocationSource
from risks.models import HazardType

class LocationView(ContextAware, LocationSource, View):

    def get(self, request, *args, **kwargs):
        reg = self.get_region(**kwargs)
        locations = self.get_location(**kwargs)
        if not locations:
            return json_response(errors=['Invalid location code'], status=404)
        loc = locations[-1]        
        app = self.get_app()
        hazard_types = HazardType.objects.filter(app=app)


        location_data = {'navItems': [location.set_app(app).set_region(reg).export() for location in locations],
                         'context': self.get_context_url(**kwargs),
                         'furtherResources': self.get_further_resources(**kwargs),
                         'overview': [ht.set_region(reg).set_location(loc).export() for ht in hazard_types]}

        return json_response(location_data)