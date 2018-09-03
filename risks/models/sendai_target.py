from django.db import models
from risks.models import Exportable


class SendaiTarget(Exportable, models.Model):
    """
    Defines indicators used by Sendai Framework for Disaster Risk Reduction - UNISDR
    """
    EXPORT_FIELDS = (('id', 'id',),
                     ('code', 'code',),
                     ('description', 'description',),                     
                     )
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, db_index=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return u"{0}".format(self.code)