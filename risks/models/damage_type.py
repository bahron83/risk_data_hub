from django.db import models


dimensions = (('dim1', 'dim1'), ('dim2', 'dim2'), ('dim3', 'dim3'))

class DamageType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False,
                            db_index=True)
    abstract = models.TextField()
    unit = models.CharField(max_length=30)    

    def __unicode__(self):
        return u"{0}".format(self.name)

class DamageTypeValue(models.Model):
    id = models.AutoField(primary_key=True)    
    dimension = models.CharField(max_length=50, choices=dimensions)
    order = models.IntegerField()
    value = models.CharField(max_length=80, null=False, blank=False,
                             db_index=True)
    axis = models.CharField(max_length=10, null=False, blank=False,
                            db_index=True)
    scenario_description = models.CharField(max_length=255, null=True, blank=True)
    layer_attribute = models.CharField(max_length=80, null=False, blank=False)
    layer_reference_attribute = models.CharField(max_length=80, null=True, blank=True)

    DIM = {'x': 'dim1', 'y': 'dim2', 'z': 'dim3'}

    # Relationships
    damage_assessment = models.ForeignKey('DamageAssessment', related_name='damagetype_association')
    damage_type = models.ForeignKey(DamageType, related_name='damageassessment_association')
    sendai_indicator = models.ForeignKey('SendaiIndicator', blank=True, null=True)

    # GeoServer Layer referenced by GeoNode resource
    resource = models.ForeignKey(
        'FurtherResource',
        blank=True,
        null=True,
        unique=False)

    def __unicode__(self):
        return u"{0}".format(self.damage_assessment.name + " - " +
                             self.damage_type.name)

    class Meta:
        """
        """
        ordering = ['order', 'value']
        db_table = 'risks_damage_type_value'

    @classmethod
    def get_axis(cls, risk):
        """
        return dimX_value for axis
        """
        return cls.objects.filter(damage_assessment=risk).order_by('order')

    def axis_to_dim(self):
        """
        return dimX_value for axis
        """
        risk = self.damage_assessment
        axis = self.get_axis(risk)
        for ax in axis:
            if self.axis == ax.axis:
                return ax.layer_attribute
        return self.DIM[self.axis]

    def axis_attribute(self):
        """
        return dX for axis
        """
        risk = self.damage_assessment
        axis = self.get_axis(risk)
        for ax in axis:
            if self.axis == ax.axis:
                return 'd{}'.format(ax.layer_attribute[3:])
        return 'd{}'.format(self.DIM[self.axis][3:])

class DymensionInfoFurtherResourceAssociation(models.Model):
    """
    Layers, Documents and other GeoNode Resources associated to:
    - A Region / Country
    - A Dymension Info
    - A Risk Analysis
    """
    id = models.AutoField(primary_key=True)

    # Relationships
    region = models.ForeignKey(
        'Region',
        blank=True,
        null=True,
        unique=False,
    )

    damage_assessment = models.ForeignKey(
        'DamageAssessment',
        blank=True,
        null=True,
        unique=False,
    )

    dimension_info = models.ForeignKey(
        'DamageType',
        blank=False,
        null=False,
        unique=False,
    )

    resource = models.ForeignKey(
        'FurtherResource',
        blank=False,
        null=False,
        unique=False)

    def __unicode__(self):
        return u"{0}".format(self.resource)

    class Meta:
        """
        """
db_table = 'risks_damage_type_further_resource_association'