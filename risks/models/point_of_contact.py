from django.db import models
from risks.models import Exportable, AdministrativeDivision, Region


class PointOfContact(Exportable, models.Model):
    """
    Risk Dataset Point of Contact; can be the poc or the author.
    """
    EXPORT_FIELDS = (('individualName', 'individual_name',),
                     ('organizationName', 'organization_name',),
                     ('positionName', 'position_name',),
                     ('deliveryPoint', 'delivery_point',),
                     ('city', 'city',),
                     ('postalCode', 'postal_code',),
                     ('email', 'e_mail',),
                     ('role', 'role',),)

    id = models.AutoField(primary_key=True)
    individual_name = models.CharField(max_length=255, null=False, blank=False)
    organization_name = models.CharField(max_length=255, null=False,
                                         blank=False)
    position_name = models.CharField(max_length=255)
    voice = models.CharField(max_length=255)
    facsimile = models.CharField(max_length=30)
    delivery_point = models.CharField(max_length=255)
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=30)
    e_mail = models.CharField(max_length=255)
    role = models.CharField(max_length=255, null=False, blank=False)
    update_frequency = models.TextField()

    # Relationships
    administrative_area = models.ForeignKey(
        AdministrativeDivision,
        null=True,
        blank=True
    )

    country = models.ForeignKey(
        Region,
        null=True,
        blank=True
    )

    def __unicode__(self):
        return u"{0}".format(self.individual_name + " - " +
                             self.organization_name)

    class Meta:
        """
        """
        db_table = 'risks_pointofcontact'