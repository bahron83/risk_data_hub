from django.db import models
from risks.models import LocationAware


class AdministrativeDataValue(models.Model):
    id = models.AutoField(primary_key=True)
    dimension = models.CharField(max_length=50, db_index=True)
    value = models.CharField(max_length=50, blank=True, null=True)    
    
    data = models.ForeignKey(
        'AdministrativeData',  
        related_name='administrativedivision_association',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )    
    adm = models.ForeignKey(
        'AdministrativeDivision',        
        related_name='data_association',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )          

    def __unicode__(self):
        return u"{0}".format(self.data.name + " - " +
                             self.adm.name)

    class Meta:
        """
        """
        db_table = 'risks_administrative_data_value'

class AdministrativeData(LocationAware, models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    indicator_type = models.CharField(max_length=50)
    unit_of_measure = models.CharField(max_length=10, blank=True, null=True)    

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """
        db_table = 'risks_administrative_data'

    def get_by_association(self):
        loc = self.get_location()
        return AdministrativeDataValue.objects.filter(adm=loc, data=self).order_by('-dimension').first()
