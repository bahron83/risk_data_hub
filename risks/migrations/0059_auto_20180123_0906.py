# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0058_auto_20180123_0803'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='hazard_type'
        ),
        migrations.AddField(
            model_name='event',
            name='hazard_type',
            field=models.ForeignKey(to='risks.HazardType'),
        ),
    ]
