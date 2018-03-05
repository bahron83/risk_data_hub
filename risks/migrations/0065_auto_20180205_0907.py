# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0064_auto_20180205_0709'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventimportdata',
            options={'ordering': ['riskapp', 'region'], 'verbose_name': 'Risks Event: Import Event Data from XLSX file', 'verbose_name_plural': 'Risks Events: Import Event Data from XLSX file'},
        ),
        migrations.RemoveField(
            model_name='eventimportdata',
            name='hazardtype',
        ),
    ]
