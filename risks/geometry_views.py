#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import logging

from django.conf import settings
from django.views.generic import TemplateView, View
from django.contrib.gis.gdal import OGRGeometry
from django.core.serializers import serialize

from geonode.utils import json_response
from risks.models import (LocationAware, Region, AdministrativeDivision)
from risks.views import AppAware

from risks.datasource import GeoserverDataSource

log = logging.getLogger(__name__)


class AdministrativeGeometry(AppAware, LocationAware, View):
    

    def _get_geometry(self, val):
        """
        converts geometry to geojson geom
        """        
        return json.loads(val.geom.ogr.json)        

    def _get_properties(self, val):
        return val.export()

    def _make_feature(self, val, app, reg):
        """
        Returns feature from the object

        """
        return {"type": "Feature",
                "properties": self._get_properties(val.set_app(app).set_region(reg)),
                "geometry": self._get_geometry(val)
                }


    def get(self, request, adm_code, **kwargs):
        try:
            app = self.get_app()
        except KeyError:
            app = None
        try:
            adm = AdministrativeDivision.objects.get(code=adm_code)
        except AdministrativeDivision.DoesNotExist:
            adm = None
        if adm is None:
            return json_response(errors=["Invalid code"], status=404)

        try:
            reg = Region.objects.get(name=kwargs['reg'])
        except Region.DoesNotExist:
            reg = None
        if reg is None:
            return json_response(errors=["Invalid region"], status=404)

        children = adm.children.all()
        _features = [adm] + list(children)

        features = [self._make_feature(item, app, reg) for item in _features]
        children_codes = [child.code for child in list(children)]
        out = {'type': 'FeatureCollection',
               'features': features,
               'childrenCodes': children_codes}
        return json_response(out)
                           

administrative_division_view = AdministrativeGeometry.as_view()
