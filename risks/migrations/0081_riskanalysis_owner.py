# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('risks', '0080_riskanalysis_show_in_event_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskanalysis',
            name='owner',
            field=models.ForeignKey(related_name='owned_risk_analysis', verbose_name=b'Owner', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
