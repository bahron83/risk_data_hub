from django.db import models
from geonode.layers.models import Layer, Style
from risks.models.risk_app import RiskAppAware
from risks.models.entity import OwnedModel, Schedulable, LocationAware, HazardTypeAware, AnalysisTypeAware, Exportable
from risks.models import HazardSet


class DamageAssessment(OwnedModel, RiskAppAware, Schedulable, LocationAware, HazardTypeAware, AnalysisTypeAware, Exportable):
    EXPORT_FIELDS = (('name', 'name',),
                     ('unitOfMeasure', 'unit_of_measure'),
                     ('hazardSet', 'get_hazard_set',),
                     ('href', 'href',),)
    EXPORT_FIELDS_EXTENDED = (('name', 'name',),
                              ('descriptorFile', 'descriptor_file',),
                              ('dataFile', 'data_file',),
                              ('metadataFile',  'metadata_file',),
                              ('layer', 'get_layer_data',),                              
                              ('hazardSet', 'get_hazard_set_extended',),
                              ('unit_of_measure', 'unit_of_measure',))

    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False,
                            db_index=True)
    unit_of_measure = models.CharField(max_length=255, null=True, blank=True)    
    tags = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=255)
    begin_date = models.DateField()
    descriptor_file = models.FileField(upload_to='descriptor_files', max_length=255)
    data_file = models.FileField(upload_to='data_files', max_length=255)
    metadata_file = models.FileField(upload_to='metadata_files', max_length=255)

    region = models.ForeignKey(
        'Region',
        related_name='damageass_region',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    
    hazard = models.ForeignKey(
        'Hazard',
        related_name='damageass_hazard',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )    
    analysis_type = models.ForeignKey(
        'AnalysisType',
        related_name='damageass_analysistype',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    layer = models.ForeignKey(
        Layer,
        blank=False,
        null=False,
        unique=False,
        related_name='base_layer'
    )
    style = models.ForeignKey(
        Style,
        blank=True,
        null=True,
        unique=False,
        related_name='style_layer'
    )
    app = models.ForeignKey('RiskApp')  

    damage_types = models.ManyToManyField('DamageType', through='DamageTypeValue')
    items = models.ManyToManyField('AssetItem', through='DamageAssessmentValue', through_fields=('damage_assessment','item'), related_name='assessment_for_item')
    phenomena = models.ManyToManyField('Phenomenon', through='DamageAssessmentValue', related_name='assessment_for_phenomenon')
    locations = models.ManyToManyField('Location', through='DamageAssessmentValue', related_name='assessment_for_location')

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """
        ordering = ['name']
        db_table = 'risks_damage_assessment'
        verbose_name_plural = 'Damage Assessments'

    def get_risk_details(self, dimension=None):
        """
        Returns dictionary with selected fields for
        """
        out = self.export(self.EXPORT_FIELDS_EXTENDED)
        return out

    def get_hazard_set_extended(self):
        return self.get_hazard_set(HazardSet.EXPORT_FIELDS_EXTENDED)

    def get_hazard_set(self, fields=None):
        hazardset = HazardSet.objects.filter(damage_assessment=self).first()        
        if hazardset:
            return hazardset.export(fields)
        return {}

    def href(self):
        reg = self.get_region()
        loc = self.get_location()
        ht = self.get_hazard_type()
        at = self.get_analysis_type()
        return self.get_url('analysis', reg.name, loc.code, ht.mnemonic, at.name, self.id)

    def get_style(self):
        if self.style:
            return {'name': self.style.name,
                    'title': self.style.sld_title,
                    'url': self.style.sld_url}
        return {}

    def get_layer_data(self):
        l = self.layer
        layer_name = l.typename
        layer_title = l.title
        layer_style = self.get_style()
        out = {'layerName': layer_name,
               'layerTitle': l.title,
               'layerStyle': layer_style}
        return out

class DamageAssessmentValue(models.Model):
    id = models.AutoField(primary_key=True)
    damage_assessment = models.ForeignKey(DamageAssessment)
    damage_type_value_1 = models.ForeignKey(
        'DamageTypeValue',
        related_name='assessment_dim1'
    )
    damage_type_value_2 = models.ForeignKey(
        'DamageTypeValue',
        related_name='assessment_dim2'
    )
    damage_type_value_3 = models.ForeignKey(
        'DamageTypeValue',
        related_name='assessment_dim3',        
        blank=True,
        null=True
    )
    phenomenon = models.ForeignKey('Phenomenon')
    item = models.ForeignKey(
        'AssetItem',
        related_name='assessed_damage',
        blank=True,
        null=True
    )
    linked_item = models.ForeignKey(
        'AssetItem',
        related_name='related_assessed_damage',
        blank=True,
        null=True
    )
    value = models.DecimalField(decimal_places=2, max_digits=10)
    #this allows to localise non static assets at the moment of the impact
    location = models.ForeignKey(
        'Location',
        related_name='damage_location',        
        blank=True,
        null=True
    )

class DamageAssessmentCreate(models.Model):
    descriptor_file = models.FileField(upload_to='descriptor_files', max_length=255)

    def file_link(self):
        if self.descriptor_file:
            return "<a href='%s'>download</a>" % (self.descriptor_file.url,)
        else:
            return "No attachment"

    file_link.allow_tags = True

    def __unicode__(self):
        return u"{0}".format(self.descriptor_file.name)

    class Meta:
        ordering = ['descriptor_file']
        db_table = 'risks_descriptor_files'
        verbose_name = 'Damage Assessment: Create new through a .ini \
                        descriptor file'
        verbose_name_plural = 'Damage Assessment: Create new through a .ini \
                               descriptor file'

class DamageAssessmentImportData(models.Model):
    data_file = models.FileField(upload_to='data_files', max_length=255)

    # Relationships
    riskapp = models.ForeignKey(
        'RiskApp',
        blank=False,
        null=False,
        unique=False,
    )

    region = models.ForeignKey(
        'Region',
        blank=False,
        null=False,
        unique=False,
    )

    damage_assessment = models.ForeignKey(
        'DamageAssessment',
        blank=False,
        null=False,
        unique=False,
    )

    def file_link(self):
        if self.data_file:
            return "<a href='%s'>download</a>" % (self.data_file.url,)
        else:
            return "No attachment"

    file_link.allow_tags = True

    def __unicode__(self):
        return u"{0}".format(self.data_file.name)

    class Meta:
        """
        """
        ordering = ['riskapp', 'region', 'damage_assessment']
        db_table = 'risks_data_files'
        verbose_name = 'Damage Assessment: Import Risk Data from XLSX file'
        verbose_name_plural = 'Damage Assessment: Import Risk Data from XLSX file'
