from django.db import models
from risks.models import RiskAppAware, HazardTypeAware, LocationAware, Exportable




class AnalysisType(RiskAppAware, HazardTypeAware, LocationAware, Exportable, models.Model):
    EXPORT_FIELDS_BASIC = (('name', 'name',),
                     ('title', 'title',),
                     ('description', 'description',),
                     ('faIcon', 'fa_icon',),)
    
    EXPORT_FIELDS = (('name', 'name',),
                     ('title', 'title',),
                     ('description', 'description',),
                     ('faIcon', 'fa_icon',),
                     ('href', 'href',),)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False,
                            db_index=True)
    title = models.CharField(max_length=80, null=False, blank=False)
    description = models.TextField(default='', null=True, blank=False)        
    fa_icon = models.CharField(max_length=30, null=True, blank=True)
    app = models.ForeignKey('RiskApp')

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """
        ordering = ['name']
        db_table = 'risks_analysis_type'

    def href(self):
        reg = self.get_region()
        loc = self.get_location()
        ht = self.get_hazard_type()
        return self.get_url('analysis_type', reg.name, loc.code, ht.mnemonic, self.name)

    def get_risk_analysis_list(self, **kwargs):
        reg = self.get_region()
        loc = self.get_location()
        ht = self.get_hazard_type().set_region(reg).set_location(loc)
        ra = self.damageass_analysistype.filter(hazard=ht,
                                                   region=reg,
                                                   administrative_divisions__in=[loc])
        if kwargs:
            ra = ra.filter(**kwargs)
        risk_analysis = [r.set_region(reg)
                          .set_location(loc)
                          .set_hazard_type(ht)
                          .set_analysis_type(self)
                         for r in ra.distinct()]
        return risk_analysis

    def get_analysis_details(self):
        risk_analysis = self.get_risk_analysis_list()
        out = self.export()
        #out['analysisClass'] = self.analysis_class.export()
        out['riskAnalysis'] = [ra.export() for ra in risk_analysis]
        return out