from django.db import models


class SendaiTarget(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False,
                            db_index=True)
    description = models.TextField(default='', null=True, blank=False)    

class SendaiIndicator(models.Model):
    id = models.AutoField(primary_key=True)
    sendai_target = models.ForeignKey(SendaiTarget)
    name = models.CharField(max_length=100, null=False, blank=False,
                            db_index=True)
    description = models.TextField(default='', null=True, blank=False)  

    def __unicode__(self):
        return u"{0}".format(self.name)  