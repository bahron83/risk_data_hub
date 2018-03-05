# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0051_auto_20180122_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='nuts3',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
