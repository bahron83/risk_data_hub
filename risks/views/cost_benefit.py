from django.views.generic import TemplateView
from risks.views.hazard_type import HazardTypeView


cost_benefit_index = TemplateView.as_view(template_name='risks/cost_benefit_index.html')

class CostBenefitAnalysisView(HazardTypeView):

    def get(self, request, *args, **kwargs):
        pass