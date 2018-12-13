from django.db import models


class AssetCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False,
                            db_index=True)

    class Meta:
        verbose_name_plural = 'Asset categories'

    def __unicode__(self):
        return u"{0}".format(self.name)