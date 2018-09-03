import logging

from django.views.decorators.cache import cache_page

from adm_lookup import *
from auth import *
from base import *
from cost_benefit import *
from data_extraction import *
from event import *
from hazard_type import *
from location import *
from pdf_report import *
from risk_index import *


log = logging.getLogger(__name__) 

CACHE_TTL = 120

location_view = cache_page(CACHE_TTL)(LocationView.as_view()) 
hazard_type_view = cache_page(CACHE_TTL)(HazardTypeView.as_view())
analysis_type_view = cache_page(CACHE_TTL)(HazardTypeView.as_view())
data_extraction = cache_page(CACHE_TTL)(DataExtractionView.as_view())
event_view = cache_page(CACHE_TTL)(EventView.as_view())
event_details_view = cache_page(CACHE_TTL)(EventDetailsView.as_view())
adm_lookup_view = cache_page(CACHE_TTL)(AdmLookupView.as_view())
auth_view = cache_page(CACHE_TTL)(AuthorizationView.as_view())

risk_layers = RiskLayersView.as_view()
pdf_report = PDFReportView.as_view()

risk_data_extraction_index = RiskIndexView.as_view()
cost_benefit_index = RiskIndexView.as_view()
risk_test_index = RiskIndexView.as_view()