from django.db import models
from risks.models import LocationAware


class AdministrativeData(LocationAware, models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    indicator_type = models.CharField(max_length=50)
    unit_of_measure = models.CharField(max_length=10, blank=True, null=True)

    administrative_divisions = models.ManyToManyField(
        "AdministrativeDivision",
        through='AdministrativeDivisionDataAssociation'        
    )

    def __unicode__(self):
        return u"{0}".format(self.name)

    def get_by_association(self):
        loc = self.get_location()
        return self.administrativedivision_association.filter(adm=loc, data=self).order_by('-dimension').first()