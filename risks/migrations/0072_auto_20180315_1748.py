# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0071_auto_20180302_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='riskanalysis',
            name='analysis_class',
        ),
        migrations.AddField(
            model_name='analysistype',
            name='analysis_class',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
