from django.db import models
from risks.models import Exportable


class AnalysisClassManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class AnalysisClass(Exportable, models.Model):
    objects = AnalysisClassManager()

    EXPORT_FIELDS = (('name', 'name',),
                    ('title', 'title',),)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False,
                            db_index=True)
    title = models.CharField(max_length=80, null=False, blank=False)

    def natural_key(self):
        return (self.name)
    
    def __unicode__(self):
        return u"{0}".format(self.name)
    
    class Meta:        
        verbose_name_plural = 'Analysis Classes'