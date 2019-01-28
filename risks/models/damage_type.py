from django.db import models
from risks.models.entity import Exportable, RiskAnalysisAware


class DamageType(Exportable, RiskAnalysisAware, models.Model):
    EXPORT_FIELDS = (('id', 'id',),
                     ('name', 'name',),
                     ('abstract', 'abstract',),
                     ('unit', 'unit',),
                     ('layers', 'get_axis_descriptions',),
                     ('values', 'get_axis_values',),
                     )
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False,
                            db_index=True)
    abstract = models.TextField()
    unit = models.CharField(max_length=30)    

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """
        ordering = ['name']
        db_table = 'risks_damagetype'

    def get_axis(self):
        risk = self.get_risk_analysis()
        return self.damageassessment_association.filter(damage_assessment=risk).order_by('order')

    def get_axis_values(self):
        axis = self.get_axis()
        return list(axis.values_list('value', flat=True))

    def get_axis_layers(self):
        axis = self.get_axis()
        return dict((a.value, a.layer.typename,) for a in axis)

    def get_axis_order(self):
        axis = self.get_axis()
        return list(axis.values_list('value', 'order'))

    def get_axis_layer_attributes(self):
        axis = self.get_axis()
        return dict((v.value, v.axis_attribute(),) for v in axis)

    def get_axis_styles(self):
        axis = self.get_axis()
        return dict((v.value, v.get_style(),) for v in axis)

    def get_axis_descriptions(self):
        axis = self.get_axis()
        out = {}
        for ax in axis:
            n = ax.value
            layer_attribute = ax.axis_attribute()
            layer_reference_attribute = ax.layer_reference_attribute
            scenario_description = ax.scenario_description
            resource = ax.resource.export() if ax.resource else None
            sendai_indicator = ax.sendai_indicator.export() if ax.sendai_indicator else None
            out[n] = {'layerAttribute': layer_attribute,
                      'layerReferenceAttribute': layer_reference_attribute,
                      'resource': resource,
                      'description': scenario_description,
                      'sendaiIndicator': sendai_indicator
                     }
        return out

class DamageTypeValue(Exportable, models.Model):
    EXPORT_FIELDS_ANALYSIS = (('damage_type', 'pdamage_type'),
                              ('id', 'id'),
                              ('axis', 'axis'),
                              ('layer_attribute', 'layer_attribute'),
                              ('value', 'value'),
                              ('sendai_indicator_id', 'psendai_indicator_id'),                              
                              )

    id = models.AutoField(primary_key=True)    
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

    @property
    def psendai_indicator_id(self):
        if self.sendai_indicator:
            return self.sendai_indicator.id

    @property
    def pdamage_type(self):        
        return self.damage_type.name
    
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