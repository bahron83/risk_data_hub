from django.db import models
from risks.models import RiskAppAware, LocationAware, Exportable, Schedulable, RiskApp, RiskAnalysis, AnalysisType


class HazardTypeManager(models.Manager):
    def get_by_natural_key(self, mnemonic):
        return self.get(mnemonic=mnemonic)

class HazardType(RiskAppAware, LocationAware, Exportable, Schedulable, models.Model):
    """
    Describes an Hazard related to an Analysis and a Risk and pointing to
    additional resources on GeoNode.
    e.g.: Earthquake, Flood, Landslide, ...
    """

    objects = HazardTypeManager()

    EXPORT_FIELDS = (('mnemonic', 'mnemonic',),
                     ('title', 'title',),
                     ('riskAnalysis', 'risk_analysis_count',),
                     ('defaultAnalysisType', 'default_analysis_type',),
                     ('href', 'href',))

    id = models.AutoField(primary_key=True)
    mnemonic = models.CharField(max_length=30, null=False, blank=False,
                                db_index=True)
    title = models.CharField(max_length=80, null=False, blank=False)
    order = models.IntegerField()
    description = models.TextField(default='')
    gn_description = models.TextField('GeoNode description', default='',
                                      null=True)
    fa_class = models.CharField(max_length=64, default='fa-times')
    app = models.ForeignKey(RiskApp)

    def __unicode__(self):
        return u"{0}".format(self.mnemonic)

    def natural_key(self):
        return (self.mnemonic)

    class Meta:
        """
        """
        ordering = ['order', 'mnemonic']
        db_table = 'risks_hazardtype'
        verbose_name_plural = 'Hazards'

    @property
    def risk_analysis_count(self):
        loc = self.get_location()
        reg = self.get_region()
        ra = RiskAnalysis.objects.filter(administrative_divisions=loc,
                                         region=reg,
                                         hazard_type=self)
        return ra.count()

    def get_analysis_types(self):
        loc = self.get_location()
        reg = self.get_region()
        ra = RiskAnalysis.objects.filter(administrative_divisions=loc,
                                         region=reg,
                                         app=self.app,
                                         hazard_type=self)

        at = AnalysisType.objects.filter(riskanalysis_analysistype__in=ra, app=self.app).distinct()
        return at

    def default_analysis_type(self):
        reg = self.get_region()
        loc = self.get_location()
        at = self.get_analysis_types()
        if at.exists():
            at = at.first()
            return {'href': self.get_url('analysis_type', reg.name, loc.code, self.mnemonic, at.name)}
        else:
            return {}

    @property
    def href(self):
        reg = self.get_region()
        loc = self.get_location()
        return self.get_url('hazard_type', reg.name, loc.code, self.mnemonic)

    def get_hazard_details(self):
        """
    "hazardType": {
        "mnemonic": "EQ",
        "description": "Lorem ipsum dolor, .....",
        "analysisTypes"[{
            "name": "loss_impact",
            "title": "Loss Impact",
            "href": "http://disasterrisk-af.geo-solutions.it/risks/risk_data_extraction/loc/AF15/ht/EQ/at/loss_impact/"
        }, {
            "name": "impact",
            "title": "Impact Analysis",
            "href": "http://disasterrisk-af.geo-solutions.it/risks/risk_data_extraction/loc/AF15/ht/EQ/at/impact/"
        }]
    },


        """
        analysis_types = self.get_analysis_types()
        reg = self.get_region()
        loc = self.get_location()
        out = {'mnemonic': self.mnemonic,
               'description': self.description,
               'analysisTypes': [at.set_region(reg).set_location(loc).set_hazard_type(self).export() for at in analysis_types]}
        return out