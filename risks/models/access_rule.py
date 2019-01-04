from django.db import models
from risks.models.analysis_type import scopes
from django.core.validators import MinValueValidator, MaxValueValidator


class AccessType(object):
    DENY = 'DENY'
    ALLOW = 'ALLOW'
    TYPES = ((DENY, DENY), (ALLOW, ALLOW),)

class AccessRule(models.Model):
    region = models.ForeignKey(
        'Region',
        related_name='access_rule',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
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
    min_adm_level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    max_adm_level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=10)
    administrative_division_regex = models.TextField(default='^.*$')
    access = models.CharField(max_length=10, choices=AccessType.TYPES)    
    order = models.IntegerField(default=0)

    class Meta:
        """
        """        
        db_table = 'risks_access_rules'        

    def __unicode__(self):
        return u"{0}".format(self.id)