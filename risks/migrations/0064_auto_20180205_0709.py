# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0063_auto_20180205_0439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='begin_date'
        ),
        migrations.AddField(
            model_name='event',
            name='begin_date',
            field=models.DateField(),
        ),
        migrations.RemoveField(
            model_name='event',
            name='end_date'
        ),
        migrations.AddField(
            model_name='event',
            name='end_date',
            field=models.DateField(),
        ),
    ]
