from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from risks.models import RiskAppAware, LocationAware, Exportable, AdministrativeData


   
class AdministrativeDivisionManager(models.Manager):
    """
    """
    def get_by_natural_key(self, code):
        return self.get(code=code)


class AdministrativeDivision(RiskAppAware, LocationAware, Exportable, MPTTModel):
    """
    Administrative Division Gaul dataset.
    """

    EXPORT_FIELDS = (('label', 'name',),
                     ('href', 'href',),
                     ('geom', 'geom_href',),
                     ('parent_geom', 'parent_geom_href',),
                     )
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30, null=False, unique=True,
                            db_index=True)
    name = models.CharField(max_length=100, null=False, blank=False,
                            db_index=True)
    # GeoDjango-specific: a geometry field (MultiPolygonField)
    # geom = gismodels.MultiPolygonField() - does not work w/ default db
    geom = models.TextField()  # As WKT
    srid = models.IntegerField(default=4326)

    level = models.IntegerField()
    # Relationships
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    
    regions = models.ManyToManyField(
        'Region',
        through='RegionAdministrativeDivisionAssociation'        
    )

    risks_analysis = models.ManyToManyField(
        'RiskAnalysis',
        through='RiskAnalysisAdministrativeDivisionAssociation'
    )

    event = models.ManyToManyField(
        'Event',
        through='EventAdministrativeDivisionAssociation'
    )

    administrative_data = models.ManyToManyField(
        'AdministrativeData',
        through='AdministrativeDivisionDataAssociation'        
    )

    @property
    def href(self):
        reg = self.get_region()
        return self.get_url('location', reg, self.code)

    @property
    def geom_href(self):
        reg = self.get_region()
        return self.get_url('geometry', reg, self.code)

    @property
    def parent_geom_href(self):
        if self.parent:
            self.parent.set_region(self.get_region())
            return self.parent.geom_href

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """
        ordering = ['code', 'name']
        db_table = 'risks_administrativedivision'
        verbose_name_plural = 'Administrative Divisions'

    class MPTTMeta:
        """
        """
        order_insertion_by = ['name']

    def get_parents_chain(self):
        parent = self.parent
        out = []
        while parent is not None:
            out.append(parent)
            parent = parent.parent
        out.reverse()
        return out


class AdministrativeDivisionMappings(models.Model):
    id = models.AutoField(primary_key=True)    
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(AdministrativeDivision, related_name='mapping_child')
    child = models.ForeignKey(AdministrativeDivision, related_name='mapping_parent')


###RELATIONS###
class AdministrativeDivisionDataAssociation(models.Model):
    id = models.AutoField(primary_key=True)
    dimension = models.CharField(max_length=50, db_index=True)
    value = models.CharField(max_length=50, blank=True, null=True)    

    #Relationships
    data = models.ForeignKey(
        AdministrativeData,  
        related_name='administrativedivision_association',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )    
    adm = models.ForeignKey(
        AdministrativeDivision,        
        related_name='data_association',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )          

    def __unicode__(self):
        return u"{0}".format(self.data.name + " - " +
                             self.adm.name)

    class Meta:
        """
        """
        db_table = 'risks_administrativedivisiondataassociation'