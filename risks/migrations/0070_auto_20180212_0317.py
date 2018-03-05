# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0069_auto_20180212_0240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='notes',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
