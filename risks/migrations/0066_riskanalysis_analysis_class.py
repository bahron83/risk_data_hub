# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0065_auto_20180205_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskanalysis',
            name='analysis_class',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
