from django.conf import settings
from django.db import models
from django.core import files
from risks.customs.custom_storage import ReplacingFileStorage


rfs = ReplacingFileStorage()

def get_default_region():
    region = Region.objects.get(name=rdh_settings.APP_DEFAULT_REGION)
    return region.id


@models.CharField.register_lookup
class UpperCase(models.Transform):
    lookup_name = 'upper'    
    bilateral = True

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "UPPER(%s)" % lhs, params

class OwnedModel(models.Model):
    @staticmethod
    def get_owner_related_name():
        return '%(app_label)s_%(class)s'
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name=get_owner_related_name.__func__(),
        verbose_name="Owner")

    class Meta:
        abstract = True


class Schedulable(models.Model):
    STATE_QUEUED = 'queued'
    STATE_PROCESSING = 'processing'
    STATE_READY = 'ready'
    STATE_ERROR = 'error'

    STATES = ((STATE_QUEUED, 'Queued',),
              (STATE_PROCESSING, 'Processing',),
              (STATE_READY, 'Ready',),
              (STATE_ERROR, 'Error',),
             )

    state = models.CharField(max_length=64, choices=STATES, null=False, default=STATE_READY)

    class Meta:
        abstract = True

    def schedule(self):
        self.refresh_from_db()
        self.set_queued()
        self.run_scheduled()

    def run_scheduled(self):
        self._run_scheduled.apply_async(args=(self,))

    def _run_scheduled(self):
        raise NotImplemented("You should override this method in subclass")

    def set_error(self):
        self.refresh_from_db()
        self.set_state(self.STATE_ERROR, save=True)


    def set_ready(self):
        self.refresh_from_db()
        self.set_state(self.STATE_READY, save=True)

    def set_queued(self):
        self.refresh_from_db()
        self.set_state(self.STATE_QUEUED, save=True)

    def set_processing(self):
        self.refresh_from_db()
        self.set_state(self.STATE_PROCESSING, save=True)

    def set_state(self, state, save=False):
        self.state = state
        if save:
            self.save()


class Exportable(object):
    EXPORT_FIELDS = []

    def export(self, fieldset=None):
        out = {}
        if fieldset is None:
            fieldset = self.EXPORT_FIELDS
        for fname, fsource in fieldset:
            val = getattr(self, fsource, None)
            if callable(val):
                val = val()
            elif isinstance(val, files.File):
                try:
                    val = val.url
                except ValueError:
                    val = None
            out[fname] = val
        return out


class HazardTypeAware(object):
    def set_hazard_type(self, ht):
        self._hazard_type = ht
        return self

    def get_hazard_type(self):
        if not getattr(self, '_hazard_type', None):
            raise ValueError("Cannot use hazard-type-less {} here".format(self.__class__.__name__))
        return self._hazard_type


class AnalysisTypeAware(object):

    def set_analysis_type(self, ht):
        self._analysis_type = ht
        return self

    def get_analysis_type(self):
        if not getattr(self, '_analysis_type', None):
            raise ValueError("Cannot use analysis-type-less {} here".format(self.__class__.__name__))
        return self._analysis_type


class RiskAnalysisAware(object):
    def set_risk_analysis(self, ht):
        self._risk_analysis = ht
        return self

    def get_risk_analysis(self):
        if not getattr(self, '_risk_analysis', None):
            raise ValueError("Cannot use analysis-type-less {} here".format(self.__class__.__name__))
        return self._risk_analysis


class LocationAware(object):

    # hack to set location context, so we can return
    # location-specific related objects
    def set_location(self, loc):
        self._location = loc
        return self

    def get_location(self):
        if not getattr(self, '_location', None):
            raise ValueError("Cannot use location-less {} here".format(self.__class__.__name__))
        return self._location

    def set_region(self, region):
        self._region = region
        return self

    def get_region(self):
        if not getattr(self, '_region', None):
            raise ValueError("Cannot use region-less {} here".format(self.__class__.__name__))
        return self._region