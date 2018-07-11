# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0085_event_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegionAdministrativeDivisionAssociation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'risks_regionadministrativedivisionassociation',
            },
        ),
        migrations.RemoveField(
            model_name='administrativedivision',
            name='region',
        ),
        migrations.RemoveField(
            model_name='region',
            name='administrative_divisions',
        ),
        migrations.AddField(
            model_name='riskanalysis',
            name='region',
            field=models.ForeignKey(related_name='riskanalysis_region', blank=True, to='risks.Region', null=True),
        ),
        migrations.AddField(
            model_name='regionadministrativedivisionassociation',
            name='administrativedivision',
            field=models.ForeignKey(to='risks.AdministrativeDivision'),
        ),
        migrations.AddField(
            model_name='regionadministrativedivisionassociation',
            name='region',
            field=models.ForeignKey(to='risks.Region'),
        ),
    ]
