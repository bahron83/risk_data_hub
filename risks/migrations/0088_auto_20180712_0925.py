# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0087_auto_20180706_1303'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventimportattributes',
            options={'ordering': ['riskapp', 'region', 'riskanalysis'], 'verbose_name': 'Risks Analysis: Import Events Data (Attributes) from XLSX file', 'verbose_name_plural': 'Risks Analysis: Import Events Data (Atributes) from XLSX file'},
        ),
        migrations.AlterModelOptions(
            name='eventimportdata',
            options={'ordering': ['riskapp', 'region'], 'verbose_name': 'Events: Import Data (Main) from XLSX file', 'verbose_name_plural': 'Events: Import Data (Main) from XLSX file'},
        ),
        migrations.AlterModelOptions(
            name='riskanalysisimportmetadata',
            options={'ordering': ['riskapp', 'region', 'riskanalysis'], 'verbose_name': 'Risks Analysis: Import or Update Metadata from                         XLSX file', 'verbose_name_plural': 'Risks Analysis: Import or Update Metadata                                from XLSX file'},
        ),
        migrations.RemoveField(
            model_name='event',
            name='people_affected',
        ),
    ]
