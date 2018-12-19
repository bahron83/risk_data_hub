from django.db import models


class Region(models.Model):
    """
    Used for handling country/regional corners
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False,
                            db_index=True)        

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        ordering = ['name']
        db_table = 'risks_region'
        verbose_name_plural = 'Regions'
        