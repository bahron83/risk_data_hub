from django.db import models
from geonode.base.models import TopicCategory
from risks.models import Exportable, PointOfContact, Region, RiskApp, FurtherResource
from risks.models.base import rfs


class HazardSet(Exportable, models.Model):
    """
    Risk Dataset Metadata.

    Assuming the following metadata model:

    Section 1: Identification
     Title  	                     [M]
     Date  	                         [M]
     Date Type                       [M]
     Edition  	                     [O]
     Abstract  	                     [M]
     Purpose  	                     [O]
    Section 2: Point of Contact
     Individual Name  	             [M]
     Organization Name               [M]
     Position Name  	             [O]
     Voice  	                     [O]
     Facsimile  	                 [O]
     Delivery Point  	             [O]
     City  	                         [O]
     Administrative Area             [O]
     Postal Code  	                 [O]
     Country  	                     [O]
     Electronic Mail Address  	     [O]
     Role  	                         [M]
     Maintenance & Update Frequency  [O]
    Section 3: Descriptive Keywords
     Keyword  	                     [O]
     Country & Regions  	         [M]
     Use constraints  	             [M]
     Other constraints  	         [O]
     Spatial Representation Type  	 [O]
    Section 4: Equivalent Scale
     Language  	                     [M]
     Topic Category Code  	         [M]
    Section 5: Temporal Extent
     Begin Date  	                 [O]
     End Date  	                     [O]
     Geographic Bounding Box  	     [M]
     Supplemental Information  	     [M]
    Section 6: Distribution Info
     Online Resource  	             [O]
     URL  	                         [O]
     Description  	                 [O]
    Section 7: Reference System Info
     Code  	                         [O]
    Section8: Data quality info
     Statement	                     [O]
    Section 9: Metadata Author
     Individual Name  	             [M]
     Organization Name  	         [M]
     Position Name  	             [O]
     Voice  	                     [O]
     Facsimile  	                 [O]
     Delivery Point  	             [O]
     City  	                         [O]
     Administrative Area  	         [O]
     Postal Code  	                 [O]
     Country  	                     [O]
     Electronic Mail Address  	     [O]
     Role  	                         [O]
    """
    EXPORT_FIELDS = (('title', 'title',),
                     ('abstract', 'abstract',),
                     ('category', 'get_category',),
                     ('fa_icon', 'get_fa_icon'),)

    EXPORT_FIELDS_EXTENDED = (('title', 'title',),
                              ('date', 'date',),
                              ('dateType', 'date_type',),
                              ('edition', 'edition',),
                              ('abstract', 'abstract',),
                              ('purpose', 'purpose',),
                              ('keyword', 'keyword',),
                              ('useConstraints', 'use_contraints',),
                              ('otherConstraints', 'other_constraints',),
                              ('spatialRepresentationType', 'spatial_representation_type',),
                              ('language', 'language',),
                              ('beginDate', 'begin_date',),
                              ('endDate', 'end_date',),
                              ('bounds', 'bounds',),
                              ('supplementalInformation', 'supplemental_information',),
                              ('onlineResource', 'online_resource',),
                              ('url', 'url',),
                              ('description', 'description',),
                              ('referenceSystemCode', 'reference_system_code',),
                              ('dataQualityStatement', 'data_quality_statement',),
                              ('pointOfContact', 'get_poc',),
                              ('author', 'get_author',),
                              ('category', 'get_category',),
                              ('country', 'get_country',),)

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    date = models.CharField(max_length=20, null=False, blank=False)
    date_type = models.CharField(max_length=20, null=False, blank=False)
    edition = models.CharField(max_length=30)
    abstract = models.TextField(null=False, blank=False)
    purpose = models.TextField()
    keyword = models.TextField()
    use_contraints = models.CharField(max_length=255, null=False, blank=False)
    other_constraints = models.CharField(max_length=255)
    spatial_representation_type = models.CharField(max_length=150)
    language = models.CharField(max_length=80, null=False, blank=False)
    begin_date = models.CharField(max_length=20)
    end_date = models.CharField(max_length=20)
    bounds = models.CharField(max_length=150, null=False, blank=False)
    supplemental_information = models.CharField(max_length=255, null=False,
                                                blank=False)
    online_resource = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    reference_system_code = models.CharField(max_length=30)
    data_quality_statement = models.TextField()

    # Relationships
    poc = models.ForeignKey(
        PointOfContact,
        related_name='point_of_contact'
    )

    author = models.ForeignKey(
        PointOfContact,
        related_name='metadata_author'
    )

    topic_category = models.ForeignKey(
        TopicCategory,
        blank=True,
        null=True,
        unique=False,
        related_name='category'
    )

    country = models.ForeignKey(
        Region,
        null=False,
        blank=False
    )

    riskanalysis = models.ForeignKey(
        'RiskAnalysis',
        related_name='riskanalysis',
        blank=False,
        null=False
    )

    def __unicode__(self):
        return u"{0}".format(self.title)

    class Meta:
        """
        """
        db_table = 'risks_hazardset'

    def get_category(self):
        return self.topic_category.identifier

    def get_fa_icon(self):
        return self.topic_category.fa_class

    def get_poc(self):
        if self.poc:
            return self.poc.export()

    def get_author(self):
        if self.author:
            self.author.export()

    def get_country(self):
        if self.country:
            self.country.name


class RiskAnalysisImportMetadata(models.Model):
    """
    """
    metadata_file = models.FileField(upload_to='metadata_files', storage=rfs, max_length=255)

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
        if self.metadata_file:
            return "<a href='%s'>download</a>" % (self.metadata_file.url,)
        else:
            return "No attachment"

    file_link.allow_tags = True

    def __unicode__(self):
        return u"{0}".format(self.metadata_file.name)

    class Meta:
        """
        """
        ordering = ['riskapp', 'region', 'riskanalysis']
        db_table = 'risks_metadata_files'
        verbose_name = 'Risks Analysis: Import or Update Metadata from \
                        XLSX file'
        verbose_name_plural = 'Risks Analysis: Import or Update Metadata \
                               from XLSX file'


###RELATIONS###
class HazardSetFurtherResourceAssociation(models.Model):
    """
    Layers, Documents and other GeoNode Resources associated to:
    - A Region / Country
    - A Hazard Set
    """
    id = models.AutoField(primary_key=True)

    # Relationships
    region = models.ForeignKey(
        Region,
        blank=True,
        null=True,
        unique=False,
    )

    hazardset = models.ForeignKey(
        HazardSet,
        blank=False,
        null=False,
        unique=False,
    )

    resource = models.ForeignKey(
        FurtherResource,
        blank=False,
        null=False,
        unique=False,
        related_name='hazard_set')

    def __unicode__(self):
        return u"{0}".format(self.resource)

    class Meta:
        """
        """
        db_table = 'risks_hazardsetfurtheresourceassociation'