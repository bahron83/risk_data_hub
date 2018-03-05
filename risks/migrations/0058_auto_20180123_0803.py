# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0057_auto_20180123_0747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='fatalities',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
