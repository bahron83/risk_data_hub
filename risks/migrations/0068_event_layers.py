# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0027_auto_20170801_1228'),
        ('risks', '0067_auto_20180206_0252'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='layers',
            field=models.ManyToManyField(to='layers.Layer', blank=True),
        ),
    ]
