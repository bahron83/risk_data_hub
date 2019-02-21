from django.db import models
from django.utils.functional import lazy
from risks.models import DamageTypeValue, Exportable


def dyminfo_values():        
    try:
        dym_infos = DamageTypeValue.objects.values('value').distinct()
        if dym_infos:
            return tuple([(str(d['value']), str(d['value'])) for d in dym_infos])    
    except:
        return []

class DataProvider(Exportable, models.Model):
    EXPORT_FIELDS = (
        ('name', 'name'),        
    )
    
    name = models.CharField(max_length=50)        

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """        
        db_table = 'risks_data_provider'        

class DataProviderMappings(Exportable, models.Model):        
    EXPORT_FIELDS = (
        ('name', 'pname'),        
        ('hazard', 'phazard'),        
        ('order', 'order'),
    )

    @property
    def pname(self):
        return self.data_provider.name

    @property
    def phazard(self):
        return self.hazard.mnemonic
    
    data_provider = models.ForeignKey(
        DataProvider,
        related_name='mappings',        
        blank=False,
        null=False,
        unique=False,
        on_delete=models.CASCADE
    )
    hazard = models.ForeignKey(
        'Hazard',
        related_name='data_provider_mappings',
        on_delete=models.CASCADE
    )
    order = models.IntegerField()
    provider_value = models.CharField(max_length=80, null=True, blank=True)
    rdh_value = models.CharField(max_length=80, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(DataProviderMappings, self).__init__(*args, **kwargs)
        self._meta.get_field('rdh_value').choices = lazy(dyminfo_values,list)()
        
    class Meta:
        db_table = 'risks_data_provider_mappings'        
        verbose_name = 'Data Provider Mappings'
        verbose_name_plural = 'Data Provider Mappings'

    def __unicode__(self):
        return u"{0} - {1}".format(self.data_provider.name, self.hazard.mnemonic)

    def get_damage_assessments(self, region, hazard_type):
        dtype_values = DamageTypeValue.objects.filter(value=self.rdh_value)
        return [d.damage_assessment for d in dtype_values if d.damage_assessment.hazard_type == hazard_type and d.damage_assessment.region == region]