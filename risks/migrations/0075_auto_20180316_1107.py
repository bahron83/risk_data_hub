# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0074_analysistype_analysis_class'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analysisclass',
            options={'verbose_name_plural': 'Analysis Classes'},
        ),
    ]
