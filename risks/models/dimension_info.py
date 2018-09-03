from django.db import models
from risks.models import RiskAnalysisAware, Exportable, Region, RiskAnalysis, FurtherResource


class DymensionInfo(RiskAnalysisAware, Exportable, models.Model):
    """
    Set of Dymensions (here we have the descriptors), to be used
    to filter SQLViews values on GeoServer.

    The multi-dimensional vectorial layer in GeoServer will be something
    like this:

       {riskanalysis, dim1, dim2, ..., dimN, value}

    A set of DymensionInfo is something like:

     {name:'Round Period', value: 'RP-10', order: 0, unit: 'Years',
      attribute_name: 'dim1'}

     {name:'Round Period', value: 'RP-20', order: 1, unit: 'Years',
      attribute_name: 'dim1'}

     {name:'Round Period', value: 'RP-50', order: 2, unit: 'Years',
      attribute_name: 'dim1'}

     {name:'Scenario', value: 'Base', order: 0, unit: 'NA',
      attribute_name: 'dim2'}

     {name:'Scenario', value: 'Scenario-1', order: 1, unit: 'NA',
      attribute_name: 'dim2'}

     {name:'Scenario', value: 'Scenraio-2', order: 2, unit: 'NA',
      attribute_name: 'dim2'}

    Values on GeoServer SQL View will be filtered like:

     {riskanalysis: risk.identifier, dim1: 'RP-10', dim2: 'Base'} -> [values]

    """
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

    # Relationships
    risks_analysis = models.ManyToManyField(
        'RiskAnalysis',
        through='RiskAnalysisDymensionInfoAssociation'
    )

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """
        ordering = ['name']
        db_table = 'risks_dymensioninfo'

    def get_axis(self):
        risk = self.get_risk_analysis()
        return self.riskanalysis_associacion.filter(riskanalysis=risk).order_by('order')

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
            scenraio_description = ax.scenraio_description
            resource = ax.resource.export() if ax.resource else None
            sendai_target = ax.sendai_target.export() if ax.sendai_target else None
            out[n] = {'layerAttribute': layer_attribute,
                      'layerReferenceAttribute': layer_reference_attribute,
                      'resource': resource,
                      'description': scenraio_description,
                      'sendaiTarget': sendai_target
                     }
        return out


###RELATIONS###
class RiskAnalysisDymensionInfoAssociation(models.Model):
    """
    Join table between RiskAnalysis and DymensionInfo
    """
    id = models.AutoField(primary_key=True)
    order = models.IntegerField()
    value = models.CharField(max_length=80, null=False, blank=False,
                             db_index=True)
    axis = models.CharField(max_length=10, null=False, blank=False,
                            db_index=True)

    # Relationships
    riskanalysis = models.ForeignKey(RiskAnalysis, related_name='dymensioninfo_associacion')
    dymensioninfo = models.ForeignKey(DymensionInfo, related_name='riskanalysis_associacion')
    scenraio_description = models.CharField(max_length=255, null=True, blank=True)
    layer_attribute = models.CharField(max_length=80, null=False, blank=False)
    layer_reference_attribute = models.CharField(max_length=80, null=True, blank=True)

    DIM = {'x': 'dim1', 'y': 'dim2', 'z': 'dim3'}

    # GeoServer Layer referenced by GeoNode resource
    resource = models.ForeignKey(
        'FurtherResource',
        blank=True,
        null=True,
        unique=False)

    # Reference to Sendai Target
    sendai_target = models.ForeignKey(
        'SendaiTarget',
        blank=True,
        null=True,
        unique=False)

    def __unicode__(self):
        return u"{0}".format(self.riskanalysis.name + " - " +
                             self.dymensioninfo.name)

    class Meta:
        """
        """
        ordering = ['order', 'value']
        db_table = 'risks_riskanalysisdymensioninfoassociation'

    @classmethod
    def get_axis(cls, risk):
        """
        return dimX_value for axis
        """
        return cls.objects.filter(riskanalysis=risk).order_by('order')

    def axis_to_dim(self):
        """
        return dimX_value for axis
        """
        risk = self.riskanalysis
        axis = self.get_axis(risk)
        for ax in axis:
            if self.axis == ax.axis:
                return ax.layer_attribute
        return self.DIM[self.axis]

    def axis_attribute(self):
        """
        return dX for axis
        """
        risk = self.riskanalysis
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
        Region,
        blank=True,
        null=True,
        unique=False,
    )

    riskanalysis = models.ForeignKey(
        RiskAnalysis,
        blank=True,
        null=True,
        unique=False,
    )

    dimension_info = models.ForeignKey(
        DymensionInfo,
        blank=False,
        null=False,
        unique=False,
    )

    resource = models.ForeignKey(
        FurtherResource,
        blank=False,
        null=False,
        unique=False)

    def __unicode__(self):
        return u"{0}".format(self.resource)

    class Meta:
        """
        """
        db_table = 'risks_dymensionfurtheresourceassociation'