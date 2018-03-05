# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0062_auto_20180131_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='area_affected',
        ),
        migrations.RemoveField(
            model_name='event',
            name='fatalities',
        ),
        migrations.RemoveField(
            model_name='event',
            name='loss_amount',
        ),
        migrations.RemoveField(
            model_name='event',
            name='loss_currency',
        ),
        migrations.RemoveField(
            model_name='event',
            name='loss_mln',
        ),
    ]
