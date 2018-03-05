# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0066_riskanalysis_analysis_class'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventImportAttributes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_file', models.FileField(max_length=255, upload_to=b'data_files')),
                ('region', models.ForeignKey(to='risks.Region')),
                ('riskanalysis', models.ForeignKey(to='risks.RiskAnalysis')),
                ('riskapp', models.ForeignKey(to='risks.RiskApp')),
            ],
            options={
                'ordering': ['riskapp', 'region', 'riskanalysis'],
                'db_table': 'risks_attribute_event_files',
                'verbose_name': 'Risks Event: Import Analysis Data (Attributes) from XLSX file',
                'verbose_name_plural': 'Risks Events: Import Analysis Data (Atributes) from XLSX file',
            },
        ),
        migrations.AlterModelOptions(
            name='eventimportdata',
            options={'ordering': ['riskapp', 'region'], 'verbose_name': 'Risks Event: Import Event Data (Main) from XLSX file', 'verbose_name_plural': 'Risks Events: Import Event Data (Main) from XLSX file'},
        ),
    ]
