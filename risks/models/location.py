from django.db import models
from django.contrib.gis.db import models as gismodels
from mptt.models import MPTTModel, TreeForeignKey
from risks.models import RiskAppAware, LocationAware, Exportable


location_types = (('fiexd_asset', 'fixed_asset'), ('non_fixed_asset', 'non_fixed_asset'), ('people', 'people'), ('damage', 'damage'),)
levels = ['continent', 'country', 'nuts2', 'nuts3', 'city', 'municipality']

class AdministrativeDivisionManager(models.Manager):
    """
    """
    def get_by_natural_key(self, code):
        return self.get(code=code)


class AdministrativeDivision(RiskAppAware, LocationAware, Exportable, MPTTModel):
    EXPORT_FIELDS = (('code', 'code',),
                     ('label', 'name',),
                     ('level', 'level',),
                     ('href', 'href',),
                     ('geom', 'geom_href',),
                     ('parent_geom', 'parent_geom_href',),
                     )
    EXPORT_FIELDS_ANALYSIS = (('id', 'id'),
                              ('code', 'code'),
                              ('name', 'name'),
                              ('parent_id', 'pparent_id'),
                              ('parent_code', 'pparent_code'),
                              ('level', 'level'),
                              )
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30, null=False, unique=True,
                            db_index=True)
    name = models.CharField(max_length=100, null=False, blank=False,
                            db_index=True)
    # GeoDjango-specific: a geometry field (MultiPolygonField)
    geom = gismodels.MultiPolygonField(srid=4326)
    level = models.IntegerField()
    # Relationships
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')

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

    @property
    def pparent_id(self):
        if self.parent:
            return self.parent.id

    @property
    def pparent_code(self):
        if self.parent:
            return self.parent.code

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

    def has_children(self):
        return self.get_children().exists()
    
    def get_children(self):
        return AdministrativeDivision.objects.filter(parent=self)

class Location(models.Model):
    id = models.AutoField(primary_key=True)
    location_type = models.CharField(max_length=50, choices=location_types)
    address = models.CharField(max_length=100)    
    lat = models.CharField(max_length=100)
    lon = models.CharField(max_length=100)
    additional_info = models.TextField(blank=True, null=True)
    administrative_division = models.ForeignKey('AdministrativeDivision', blank=True, null=True)

    def __unicode__(self):
        return u"type: {0} - adm_unit: {1} - lat: {2} - lon: {3}".format(self.location_type, self.administrative_division, self.lat, self.lon)

    class Meta:
        """
        """
        unique_together = ("lat", "lon", "administrative_division")
        