# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0091_administrativedata_indicator_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskanalysis',
            name='tags',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
