from django.db import models
from django.contrib.auth.models import UserManager
from geonode.people.models import Profile
from risks.models import Region
from risks.models.analysis_type import scopes



class AccessType(object):
    DENY = 'DENY'
    ALLOW = 'ALLOW'
    TYPES = ((DENY, DENY), (ALLOW, ALLOW),)

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

class AccessRule(models.Model):
    scope = models.CharField(max_length=25, blank=True, null=True, choices=scopes)
    damage_assessment = models.ForeignKey(
        'DamageAssessment',
        related_name='access_rule',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    group = models.ForeignKey(
        'RdhGroup',
        related_name='access_rule',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        'RdhUser',
        related_name='access_rule',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    min_adm_level = models.IntegerField(default=0)
    max_adm_level = models.IntegerField(default=10)
    administrative_division_regex = models.TextField()
    access = models.CharField(max_length=10, choices=AccessType.TYPES)    

    class Meta:
        """
        """        
        db_table = 'risks_access_rules'        

    def __unicode__(self):
        return u"{0}".format(self.id) 
    