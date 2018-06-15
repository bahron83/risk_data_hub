# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0078_auto_20180607_1428'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='riskanalysis',
            name='matching_ra',
        ),
    ]
