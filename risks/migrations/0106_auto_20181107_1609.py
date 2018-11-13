# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0105_auto_20181107_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_id',
            field=models.CharField(db_index=True, max_length=25, null=True, blank=True),
        ),
    ]
