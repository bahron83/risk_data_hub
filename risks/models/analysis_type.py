from django.db import models
from risks.models import (RiskAppAware, HazardTypeAware, LocationAware, Exportable, RiskApp,
                            FurtherResource, AnalysisClass)


class AnalysisType(RiskAppAware, HazardTypeAware, LocationAware, Exportable, models.Model):
    """
    For Risk Data Extraction it can be, as an instance, 'Loss Impact', 'Impact
    Analysis'. This object should also refer to any additional description
    and/or related resource useful to the users to get details on the
    Analysis type.
    """
    EXPORT_FIELDS = (('name', 'name',),
                     ('title', 'title',),
                     ('description', 'description',),
                     ('faIcon', 'fa_icon',),
                     ('href', 'href',),
                     ('analysisClass', 'get_analysis_class_export',),)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False,
                            db_index=True)
    title = models.CharField(max_length=80, null=False, blank=False)
    description = models.TextField(default='', null=True, blank=False)
    app = models.ForeignKey(RiskApp)
    analysis_class = models.ForeignKey(AnalysisClass, null=True)
    fa_icon = models.CharField(max_length=30, null=True, blank=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        """
        """
        ordering = ['name']
        db_table = 'risks_analysistype'

    def href(self):
        reg = self.get_region()
        loc = self.get_location()
        ht = self.get_hazard_type()
        return self.get_url('analysis_type', reg.name, loc.code, ht.mnemonic, self.name)

    def get_risk_analysis_list(self, **kwargs):
        reg = self.get_region()
        loc = self.get_location()
        ht = self.get_hazard_type().set_region(reg).set_location(loc)
        ra = self.riskanalysis_analysistype.filter(hazard_type=ht,
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

    def get_analysis_class_export(self):
        return self.analysis_class.export()


###RELATIONS###
class AnalysisTypeFurtherResourceAssociation(models.Model):
    """
    Layers, Documents and other GeoNode Resources associated to:
    - A Region / Country
    - An Hazard
    - An Analysis Type
    """
    id = models.AutoField(primary_key=True)

    # Relationships
    region = models.ForeignKey(
        'Region',
        blank=True,
        null=True,
        unique=False,
    )

    hazard_type = models.ForeignKey(
        'HazardType',
        blank=True,
        null=True,
        unique=False,
    )

    analysis_type = models.ForeignKey(
        AnalysisType,
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
        db_table = 'risks_analysisfurtheresourceassociation'