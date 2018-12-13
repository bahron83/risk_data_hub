from django.db import models


class Owner(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"{0}".format(self.name)