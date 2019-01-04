from django.db import models
from risks.models import DamageTypeValue


def dyminfo_values():        
    try:
        dym_infos = DamageTypeValue.objects.values('value').distinct()
        if dym_infos:
            return tuple([(str(d['value']), str(d['value'])) for d in dym_infos])    
    except:
        return ()

class DataProvider(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """        
        db_table = 'risks_data_provider'        

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
        db_table = 'risks_data_provider_mappings'        
        verbose_name = 'DataProviderMappings'
        verbose_name_plural = 'DataProviderMappings'

    def get_damage_assessments(self, region, hazard_type):
        dtype_values = DamageTypeValue.objects.filter(value=self.rdh_value)
        return [d.damage_assessment for d in dtype_values if d.damage_assessment.hazard_type == hazard_type and d.damage_assessment.region == region]