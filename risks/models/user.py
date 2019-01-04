from collections import namedtuple
from django.db import models
from django.contrib.auth.models import UserManager
from geonode.people.models import Profile
from risks.models import Region


class RdhUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)

class RdhUser(Profile):    
    region = models.ForeignKey(
        Region,
        related_name='user_in_region',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )        

    objects = RdhUserManager()

class RdhGroup(models.Model):
    name = models.CharField(max_length=50)
    region = models.ForeignKey(
        Region,
        related_name='group_in_region',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )    
    users = models.ManyToManyField(RdhUser)

def get_generic_filter():
    d = {}
    for field in AccessRule._meta.get_fields():
        d[field.name] = []
    qfilter = namedtuple("GenericFilter", d.keys())(*d.values())
    return qfilter