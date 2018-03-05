# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0059_auto_20180123_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='begin_date',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.CharField(max_length=20),
        ),
    ]
