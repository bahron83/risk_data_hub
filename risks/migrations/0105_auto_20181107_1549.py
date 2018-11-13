# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0104_auto_20181107_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_id',
            field=models.CharField(unique=True, max_length=25, db_index=True),
        ),
        migrations.AddField(
            model_name='event',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
