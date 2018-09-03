from django.db import models
from django.db.models import Q
from geonode.base.models import ResourceBase
from risks.models import OwnedModel


class FurtherResource(OwnedModel, models.Model):
    """
    Additional GeoNode Resources which can be associated to:
    - A Region / Country
    - An Hazard
    - An Analysis Type
    - A Dymension Info
    - A Risk Analysis
    """

    id = models.AutoField(primary_key=True)
    text = models.TextField()

    # Relationships
    resource = models.ForeignKey(
        ResourceBase,
        blank=False,
        null=False,
        unique=False,
        related_name='resource')

    def __unicode__(self):
        return u"{0}".format(self.resource.title)

    class Meta:
        """
        """
        db_table = 'risks_further_resource'

    def export(self):
        """
        returns simplified dictionary, json-friendly
        """
        r = self.resource

        out = {'date': r.date.strftime('%Y%m%d'),
               'title': r.title,
               'text': self.text,
               'abstract': r.abstract,
               'uuid': r.uuid,
               'license': r.license_light,
               'category': r.category.description if r.category else None,
               'is_published': r.is_published,
               'thumbnail': r.get_thumbnail_url(),
               # 'downloads': r.download_links(),
               'details': r.detail_url}
        return out

    @classmethod
    def for_analysis_type(cls, atype, region=None, htype=None):
        """
        .. py:classmethod: for_analysis_type(atype, region=None, htype=None)

        Return list of :py:class:FurtherResorce that are associated with
        Analysis type. List may be filtered by region and hazard type.

        :param atype: Analysis Type
        :param region: Region
        :param htype: Hazard type
        :type atype: :py:class:AnalysisType
        :type region: :py:class:geonode.base.models.Region
        :type htype: :py:class:HazardType

        """
        qparams = Q(analysistypefurtherresourceassociation__analysis_type=atype)
        if region is not None:
            qparams = qparams & Q(Q(analysistypefurtherresourceassociation__region=region)|Q(analysistypefurtherresourceassociation__region__isnull=True))
        else:
            qparams = qparams & Q(analysistypefurtherresourceassociation__region__isnull=True)
        if htype is not None:
            qparams = qparams & Q(Q(analysistypefurtherresourceassociation__hazard_type=htype)|Q(analysistypefurtherresourceassociation__hazard_type__isnull=True))
        else:
            qparams = qparams & Q(analysistypefurtherresourceassociation__hazard_type__isnull=True)
        return cls.objects.filter(qparams).distinct()

    @classmethod
    def for_dymension_info(cls, dyminfo, region=None, ranalysis=None):
        """
        .. py:classmethod: for_dymension_info(dyminfo, region=None, ranalysis=None)

        Return list of :py:class:FurtherResorce that are associated with
        Dymension Info. List may be filtered by region and risk analysis.

        :param dyminfo: Dymension Info
        :param region: Region
        :param ranalysis: Risk Analysis
        :type dyminfo: :py:class:DymensionInfo
        :type region: :py:class:geonode.base.models.Region
        :type ranalysis: :py:class:RiskAnalysis

        """
        qparams = Q(dymensioninfofurtherresourceassociation__dimension_info=dyminfo)
        if region is not None:
            qparams = qparams & Q(Q(dymensioninfofurtherresourceassociation__region__isnull=True)|Q(dymensioninfofurtherresourceassociation__region=region))
        else:
            qparams = qparams & Q(dymensioninfofurtherresourceassociation__region__isnull=True)

        if ranalysis is not None:
            qparams = qparams & Q(Q(dymensioninfofurtherresourceassociation__riskanalysis__isnull=True)|Q(dymensioninfofurtherresourceassociation__riskanalysis=ranalysis))
        else:
            qparams = qparams & Q(dymensioninfofurtherresourceassociation__riskanalysis__isnull = True)
        return cls.objects.filter(qparams).distinct()

    @classmethod
    def for_hazard_set(cls, hset, region=None):
        """
        .. py:classmethod: for_hazard_set(hset, region=None)

        Returns list of :py:class:FurtherResource associated with
        Hazard Set. List may be filtered by region.

        :param hset: Hazard Type
        :param region: region to filter by
        :type hset: :py:class:HazardSet
        :type region: :py:class:geonode.base.models.Region


        """
        qparams = Q(hazard_set__hazardset=hset)
        if region is not None:
            qparams = qparams & Q(Q(hazard_set__region=region)|Q(hazard_set__region__isnull=True))
        else:
            qparams = qparams & Q(hazard_set__region__isnull=True)

        return cls.objects.filter(qparams).distinct()