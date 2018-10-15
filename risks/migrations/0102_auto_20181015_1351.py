# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0101_eventimportattributes_adm_level_precision'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventFurtherAdministrativeDivisionAssociation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'risks_eventfurtheradministrativedivisionassociation',
            },
        ),
        migrations.AlterModelOptions(
            name='event',
            options={},
        ),
        migrations.AlterModelOptions(
            name='eventimportattributes',
            options={'ordering': ['riskapp', 'region', 'riskanalysis', 'adm_level_precision'], 'verbose_name': 'Risks Analysis: Import Events Data (Attributes) from XLSX file', 'verbose_name_plural': 'Risks Analysis: Import Events Data (Atributes) from XLSX file'},
        ),
        migrations.AddField(
            model_name='eventfurtheradministrativedivisionassociation',
            name='event',
            field=models.ForeignKey(to='risks.Event'),
        ),
        migrations.AddField(
            model_name='eventfurtheradministrativedivisionassociation',
            name='f_adm',
            field=models.ForeignKey(to='risks.AdministrativeDivisionMappings'),
        ),
        migrations.AddField(
            model_name='event',
            name='further_administrative_divisions',
            field=models.ManyToManyField(related_name='event_further_adm', through='risks.EventFurtherAdministrativeDivisionAssociation', to='risks.AdministrativeDivisionMappings'),
        ),
    ]
