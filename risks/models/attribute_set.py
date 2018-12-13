from django.db import models


class AttributeSet(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    attributes = models.ManyToManyField('EavAttribute')

    def __unicode__(self):
        return u"{0}".format(self.name)