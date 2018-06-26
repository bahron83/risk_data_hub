# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('risks', '0083_administrativedata_unit_of_measure'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='owner',
            field=models.ForeignKey(related_name='risks_region', verbose_name=b'Owner', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='riskanalysis',
            name='owner',
            field=models.ForeignKey(related_name='risks_riskanalysis', verbose_name=b'Owner', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
