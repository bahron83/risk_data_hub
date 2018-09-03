import json
from django.conf import settings
from django.views.generic import TemplateView
from risks.views.base import AppAware, FeaturesSource
from risks.models import RiskApp


class RiskIndexView(AppAware, FeaturesSource, TemplateView):

    TEMPLATES = {RiskApp.APP_DATA_EXTRACTION: 'risks/risk_data_extraction_index.html',
                 RiskApp.APP_COST_BENEFIT: 'risks/cost_benefit_index.html',
                 RiskApp.APP_TEST: 'risks/risk_test_index.html'}

    def get_template_names(self):
        app = self.get_app()
        return [self.TEMPLATES[app.name]]

    def get_context_data(self, *args, **kwargs):
        ctx = super(RiskIndexView, self).get_context_data(*args, **kwargs)
        ctx['app'] = app = self.get_app()

        app_ctx = {'app': app.name,
                   'geometry': app.url_for('geometry', settings.RISKS['DEFAULT_LOCATION']),
                   'region': settings.RISKS['DEFAULT_LOCATION'],
                   'href': app.href}
        ctx['app_ctx'] = json.dumps(app_ctx)

        return ctx