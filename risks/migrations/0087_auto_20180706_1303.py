# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0086_auto_20180706_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativedivision',
            name='regions',
            field=models.ManyToManyField(to='risks.Region', through='risks.RegionAdministrativeDivisionAssociation'),
        ),
        migrations.AddField(
            model_name='region',
            name='administrative_divisions',
            field=models.ManyToManyField(related_name='administrative_divisions', through='risks.RegionAdministrativeDivisionAssociation', to='risks.AdministrativeDivision'),
        ),
    ]
