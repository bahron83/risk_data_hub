#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from risks import views
from risks import geometry_views
from risks.models import RiskApp

KWARGS_DATA_EXTRACTION = {'app': RiskApp.APP_DATA_EXTRACTION}
KWARGS_COST_BENEFIT_ANALYSIS = {'app': RiskApp.APP_COST_BENEFIT}
KWARGS_TEST = {'app': RiskApp.APP_TEST}



geometry_urls = [
    url(r'reg/(?P<reg>[\w\-]+)/loc/(?P<adm_code>[\w\-]+)/$', geometry_views.administrative_division_view, name='location'),
]
api_urls = [
    url(r'risk/(?P<risk_id>[\d]+)/layers/$', views.risk_layers, name='layers'),
]

urlpatterns = [
    url(r'^geom/', include(geometry_urls, namespace="geom")),
    url(r'^api/', include(api_urls, namespace='api')),
]

_urls = (
    (r'^$', views.risk_data_extraction_index, 'index',),
    (r'^reg/(?P<reg>[\w\-]+)/geom/(?P<adm_code>[\w\-]+)/$', geometry_views.administrative_division_view, 'geometry',),
    (r'^geom/(?P<adm_code>[\w\-]+)/$', geometry_views.administrative_division_view, 'geometry',),
    (r'reg/(?P<reg>[\w\-]+)/loc/(?P<loc>[\w\-]+)/$', views.location_view, 'location',),
    (r'loc/(?P<loc>[\w\-]+)/$', views.location_view, 'location',),    
    (r'reg/(?P<reg>[\w\-]+)/loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/$', views.hazard_type_view, 'hazard_type',),
    (r'loc/(?P<loc>[\w\-]+)/lvl/(?P<lvl>[\w\-]+)/ht/(?P<ht>[\w\-]+)/an/(?P<an>[\w\-]+)/evt/(?P<evt>[\w\-]+)/$', views.event_view, 'event',),
    (r'ht/(?P<ht>[\w\-]+)/an/(?P<an>[\w\-]+)/evt/(?P<evt>[\w\-]+)/$', views.event_details_view, 'event_details',),
    (r'reg/(?P<reg>[\w\-]+)/loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/$', views.hazard_type_view, 'analysis_type',),
    (r'reg/(?P<reg>[\w\-]+)/loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/an/(?P<an>[\w\-]+)/$', views.data_extraction, 'analysis',),
    (r'reg/(?P<reg>[\w\-]+)/loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/an/(?P<an>[\w\-]+)/load/(?P<load>[\w\-]+)/$', views.data_extraction, 'analysis_all',),
    (r'reg/(?P<reg>[\w\-]+)/loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/an/(?P<an>[\w\-]+)/from/(?P<from>[\w\-]+)/to/(?P<to>[\w\-]+)/$', views.data_extraction, 'analysis_daterange',),
    (r'loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/an/(?P<an>[\w\-]+)/dym/(?P<dym>[\w\-]+)$', views.data_extraction, 'analysis_dym',),
    #(r'apps/(?P<apps>[\w\-]+)/?$', views.apps_view, 'apps',),
    (r'countryauth/?$', views.auth_view, 'countryauth',),
    (r'admlookup/(?P<admlookup>[\w\-]+)/?$', views.adm_lookup_view, 'admlookup',),
    (r'reg/(?P<reg>[\w\-]+)/loc/(?P<loc>[\w\-]+)/detail/(?P<detail>[\w\-]+)/?$', views.adm_lookup_view, 'admlookup',),    
    (r'loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/an/(?P<an>[\w\-]+)/pdf/$', views.pdf_report, 'pdf_report',),
    (r'loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/an/(?P<an>[\w\-]+)/pdf/(?P<pdf_part>({}))/$'\
        .format('|'.join(views.PDFReportView.PDF_PARTS)), views.pdf_report, 'pdf_report_part',),)

urls_sets = ((RiskApp.APP_DATA_EXTRACTION, KWARGS_DATA_EXTRACTION,),
             (RiskApp.APP_COST_BENEFIT, KWARGS_COST_BENEFIT_ANALYSIS,),
             (RiskApp.APP_TEST, KWARGS_TEST,))


for app_name, kwargs in urls_sets:
    urllist = []
    for r in _urls:
        uname = r[-1]
        r = r[:-1]
        u = url(*r, name=uname, kwargs=kwargs)
        urllist.append(u)
    new_urls = url(r'^{}/'.format(app_name), include(urllist, namespace=app_name))
    urlpatterns.append(new_urls)

