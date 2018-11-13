from django.db import models
from risks.models import RiskAnalysisDymensionInfoAssociation


def dyminfo_values():        
    dym_infos = RiskAnalysisDymensionInfoAssociation.objects.values('value').distinct()
    return tuple([(str(d['value']), str(d['value'])) for d in dym_infos])

class DataProvider(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """        
        db_table = 'risks_dataprovider'        

class DataProviderMappings(models.Model):        
    data_provider = models.ForeignKey(
        DataProvider,
        blank=False,
        null=False,
        unique=False
    )
    provider_value = models.CharField(max_length=80)
    rdh_value = models.CharField(max_length=80, choices=dyminfo_values())
        
    class Meta:
        verbose_name = 'DataProviderMappings'
        verbose_name_plural = 'DataProviderMappings'

    def get_risk_analysis(self, region, hazard_type):
        dyminfo_values = RiskAnalysisDymensionInfoAssociation.objects.filter(value=self.rdh_value)
        return [d.riskanalysis for d in dyminfo_values if d.riskanalysis.hazard_type == hazard_type and d.riskanalysis.region == region]