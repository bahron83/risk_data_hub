from django.db import models
from geonode.layers.models import Layer, Style
from risks.models import (OwnedModel, RiskAppAware, Schedulable, LocationAware, 
                            HazardTypeAware, AnalysisTypeAware, Exportable, RiskApp, 
                            AdministrativeDivision, HazardSet)
from risks.models.base import rfs


class RiskAnalysis(OwnedModel, RiskAppAware, Schedulable, LocationAware, HazardTypeAware, AnalysisTypeAware, Exportable, models.Model):
    """
    A type of Analysis associated to an Hazard (Earthquake, Flood, ...) and
    an Administrative Division.

    It defines a set of Dymensions (here we have the descriptors), to be used
    to filter SQLViews values on GeoServer.
    """

    EXPORT_FIELDS = (('name', 'name',),
                     ('unitOfMeasure', 'unit_of_measure'),
                     ('hazardSet', 'get_hazard_set',),
                     ('href', 'href',),)
    EXPORT_FIELDS_EXTENDED = (('name', 'name',),
                              ('descriptorFile', 'descriptor_file',),
                              ('dataFile', 'data_file',),
                              ('metadataFile',  'metadata_file',),
                              ('layer', 'get_layer_data',),
                              ('referenceLayer', 'get_reference_layer_data',),
                              ('referenceStyle', 'get_reference_style',),
                              ('additionalTables', 'get_additional_data',),
                              ('hazardSet', 'get_hazard_set_extended',),
                              ('unit_of_measure', 'unit_of_measure',))

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False,
                            db_index=True)
    unit_of_measure = models.CharField(max_length=255, null=True, blank=True)
    show_in_event_details = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, null=True, blank=True)
    descriptor_file = models.FileField(upload_to='descriptor_files', max_length=255)
    data_file = models.FileField(upload_to='data_files', max_length=255)
    metadata_file = models.FileField(upload_to='metadata_files', max_length=255)

    #analysis_class = models.CharField(max_length=50, null=True, blank=True)   

    # Relationships
    region = models.ForeignKey(
        'Region',
        related_name='riskanalysis_region',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    analysis_type = models.ForeignKey(
        'AnalysisType',
        related_name='riskanalysis_analysistype',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    hazard_type = models.ForeignKey(
        'HazardType',
        related_name='riskanalysis_hazardtype',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    hazardset = models.ForeignKey(
        'HazardSet',
        related_name='hazardset',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )    

    administrative_divisions = models.ManyToManyField(
        "AdministrativeDivision",
        through='RiskAnalysisAdministrativeDivisionAssociation'
    )

    dymension_infos = models.ManyToManyField(
        "DymensionInfo",
        through='RiskAnalysisDymensionInfoAssociation'
    )

    events = models.ManyToManyField(
        'Event',
        through='EventRiskAnalysisAssociation'        
    )     

    layer = models.ForeignKey(
        Layer,
        blank=False,
        null=False,
        unique=False,
        related_name='base_layer'
    )

    style = models.ForeignKey(Style,
                              blank=True,
                              null=True,
                              unique=False,
                              related_name='style_layer'
    )

    reference_layer = models.ForeignKey(
        Layer,
        blank=True,
        null=True,
        unique=False,
        related_name='reference_layer'
    )

    reference_style = models.ForeignKey(Style,
                              blank=True,
                              null=True,
                              unique=False,
                              related_name='style_reference_layer'
    )

    additional_layers = models.ManyToManyField(Layer, blank=True)    
    app = models.ForeignKey(RiskApp)  

    @staticmethod
    def get_owner_related_name():
        return 'owned_risk_analysis'  

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """
        ordering = ['name']
        db_table = 'risks_riskanalysis'
        verbose_name_plural = 'Risks Analysis'

    def get_risk_details(self, dimension=None):
        """
        Returns dictionary with selected fields for
        """
        out = self.export(self.EXPORT_FIELDS_EXTENDED)
        return out

    def get_hazard_set_extended(self):
        return self.get_hazard_set(HazardSet.EXPORT_FIELDS_EXTENDED)

    def get_hazard_set(self, fields=None):
        if self.hazardset:
            return self.hazardset.export(fields)
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

    def get_reference_style(self):
        if self.reference_style:
            return {'name': self.reference_style.name,
                    'title': self.reference_style.sld_title,
                    'url': self.reference_style.sld_url}
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

    def get_reference_layer_data(self):
        if self.reference_layer:
            l = self.reference_layer
            layer_name = l.typename
            layer_title = l.title
            layer_style = self.get_style()
            out = {'layerName': layer_name,
                   'layerTitle': l.title,
                   'layerStyle': layer_style}
            return out
        return {}

    def get_additional_data(self):
        out = []
        for at in self.additional_data.all():
            at_data = at.export()
            out.append(at_data)
        return out


class RiskAnalysisCreate(models.Model):
    descriptor_file = models.FileField(upload_to='descriptor_files', storage=rfs, max_length=255)

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
        verbose_name = 'Risks Analysis: Create new through a .ini \
                        descriptor file'
        verbose_name_plural = 'Risks Analysis: Create new through a .ini \
                               descriptor file'


class RiskAnalysisImportData(models.Model):
    data_file = models.FileField(upload_to='data_files', storage=rfs, max_length=255)

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

    riskanalysis = models.ForeignKey(
        'RiskAnalysis',
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
        ordering = ['riskapp', 'region', 'riskanalysis']
        db_table = 'risks_data_files'
        verbose_name = 'Risks Analysis: Import Risk Data from XLSX file'
        verbose_name_plural = 'Risks Analysis: Import Risk Data from XLSX file'


###RELATIONS###
class RiskAnalysisAdministrativeDivisionAssociation(models.Model):
    """
    Join table between RiskAnalysis and AdministrativeDivision
    """
    id = models.AutoField(primary_key=True)

    # Relationships
    riskanalysis = models.ForeignKey(RiskAnalysis)
    administrativedivision = models.ForeignKey(AdministrativeDivision)

    def __unicode__(self):
        return u"{0}".format(self.riskanalysis.name + " - " +
                             self.administrativedivision.name)

    class Meta:
        """
        """
        db_table = 'risks_riskanalysisadministrativedivisionassociation'