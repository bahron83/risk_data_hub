# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0052_event_nuts3'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventImportData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_file', models.FileField(max_length=255, upload_to=b'data_files')),
                ('hazardtype', models.ForeignKey(to='risks.HazardType')),
                ('region', models.ForeignKey(to='risks.Region')),
                ('riskapp', models.ForeignKey(to='risks.RiskApp')),
            ],
            options={
                'ordering': ['riskapp', 'region', 'hazardtype'],
                'db_table': 'risks_data_event_files',
                'verbose_name': 'Risks Event: Import Event Data from XLSX file',
                'verbose_name_plural': 'Risks Events: Import Event Data from XLSX file',
            },
        ),
    ]
