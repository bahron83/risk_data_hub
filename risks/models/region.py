from django.db import models
from risks.models import OwnedModel, AdministrativeDivision


class Region(OwnedModel, models.Model):
    """
    Groups a set of AdministrativeDivisions
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False,
                            db_index=True)
    # level:
    # 0 is global
    # 1 is continent
    # 2 is sub-continent
    # 3 is country
    level = models.IntegerField(null=False, blank=False, db_index=True)

    # Relationships
    administrative_divisions = models.ManyToManyField(
        'AdministrativeDivision',
        through='RegionAdministrativeDivisionAssociation',
        related_name='administrative_divisions'
    )

    @staticmethod
    def get_owner_related_name():
        return 'owned_region'    

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        ordering = ['name', 'level']
        db_table = 'risks_region'
        verbose_name_plural = 'Regions'


###RELATIONS###
class RegionAdministrativeDivisionAssociation(models.Model):

    id = models.AutoField(primary_key=True)

    # Relationships
    region = models.ForeignKey(Region)
    administrativedivision = models.ForeignKey(AdministrativeDivision)

    def __unicode__(self):
        return u"{0}".format(self.region.name + " - " +
                             self.administrativedivision.name)

    class Meta:
        """
        """
        db_table = 'risks_regionadministrativedivisionassociation'