import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField
from geonode.layers.models import Layer, Style
from risks.models.risk_app import RiskAppAware
from risks.models.entity import OwnedModel, Schedulable, LocationAware, HazardTypeAware, AnalysisTypeAware, Exportable
from risks.models import HazardSet
from risks.models.location import levels as adm_levels


class DamageAssessment(OwnedModel, RiskAppAware, Schedulable, LocationAware, HazardTypeAware, AnalysisTypeAware, Exportable):
    """
    JSON schema of object in values field (array of objects)
    {
        "region":"Europe",
        "damage_assessment":"Potential_Impact_flood_on_esmCommercial",
        "dim1": {
            "id": "1",
            "dim_id": "1",
            "sendai_indicator_id": "1",
            "dimension": "dim1",
            "value": "rural buildings",
        },
        "dim2": {
            "id": "2",
            "dim_id": "2",			
            "dimension": "dim2",
            "value": "10 years",
        },
        "dim3": {},
        "phenomenon": {
            "id": "1", 
            "event_id":"1"           
            "value": "0.5"
        },
        "year":"2016",
        "item_id": "1",
        "linked_item_id": "2",
        "value": "10.7",
        "location": {
            "id": "1",
            "geom": "geojson representation",
            "address": "some address",
            "notes": "blabla"
        },
        "administrative_division": {
            "id": "10",
            "code": "IT015",
            "name": "Verona"
            "parent_id": "1",
            "parent_code": "IT"
            "level": "2",
        },
        "geometry":"geom.WKT",
    }
    """
    
    EXPORT_FIELDS = (('name', 'name',),
                     ('unitOfMeasure', 'unit_of_measure'),
                     ('hazardSet', 'export_hazard_set',),
                     ('href', 'href',),)
    EXPORT_FIELDS_EXTENDED = (('name', 'name',),
                              ('descriptorFile', 'descriptor_file',),
                              ('dataFile', 'data_file',),
                              ('metadataFile',  'metadata_file',),
                              ('layer', 'get_layer_data',),                              
                              ('hazardSet', 'export_hazard_set_extended',),
                              ('unit_of_measure', 'unit_of_measure',))

    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False,
                            db_index=True)
    unit_of_measure = models.CharField(max_length=255, null=True, blank=True)    
    tags = models.CharField(max_length=255, null=True, blank=True)    
    assessment_date = models.DateField()
    insert_date = models.DateField(default=datetime.date.today)    
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
    style = models.ForeignKey(
        'Style',
        related_name='damageassessment_association',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )
    additional_layers = models.ManyToManyField(Layer, blank=True)
    app = models.ForeignKey('RiskApp')  

    damage_types = models.ManyToManyField('DamageType', through='DamageTypeValue')
    '''items = models.ManyToManyField('AssetItem', through='DamageAssessmentValue', through_fields=('damage_assessment','item'), related_name='assessment_for_item')
    phenomena = models.ManyToManyField('Phenomenon', through='DamageAssessmentValue', related_name='assessment_for_phenomenon')
    locations = models.ManyToManyField('Location', through='DamageAssessmentValue', related_name='assessment_for_location')
    '''
    #values = JSONField(null=True, blank=True)
    
    administrative_divisions = models.ManyToManyField('AdministrativeDivision', related_name='assessment_adm_division')
    users = models.ManyToManyField('RdhUser', through='AccessRule', through_fields=('damage_assessment', 'user'), related_name='damage_assessment_user_access')
    groups = models.ManyToManyField('RdhGroup', through='AccessRule', through_fields=('damage_assessment', 'group'), related_name='damage_assessment_group_access')

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

    def export_hazard_set_extended(self):
        return self.export_hazard_set(HazardSet.EXPORT_FIELDS_EXTENDED)

    def export_hazard_set(self, fields=None):
        hazardset = self.get_hazard_set()
        if hazardset:
            return hazardset.export(fields)
        return {}

    def get_hazard_set(self):
        return HazardSet.objects.filter(damage_assessment=self).first()        

    def href(self):
        reg = self.get_region()
        loc = self.get_location()
        ht = self.get_hazard_type()
        at = self.get_analysis_type()
        return self.get_url('analysis', reg.name, loc.code, ht.mnemonic, at.name, self.id)

    

class DamageAssessmentEntry(models.Model):
    id = models.AutoField(primary_key=True)
    entry = JSONField()
    '''damage_assessment = models.ForeignKey(DamageAssessment)
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
    )'''

    class Meta:
        """
        """        
        db_table = 'risks_damage_assessment_entry'
        verbose_name_plural = 'Damage Assessment Entries'

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

class Style(models.Model):
    name = models.CharField(max_length=100)
    content = JSONField()

    def sync_details_field(self):
        content = {}
        if self.content:
            content = dict(self.content)
        for attr in adm_levels:
            if attr not in content.keys():
                content[attr] = ''
        Style.objects.filter(pk=self.id).update(content=content)

    def custom_export(self):
        json_exp = {}
        for l in adm_levels:
            if l in self.content:                 
                adm_level_index = str(adm_levels.index(l))
                json_exp[adm_level_index] = self.content[l]                
        return json_exp

    def __unicode__(self):
        return u"{0}".format(self.name)
