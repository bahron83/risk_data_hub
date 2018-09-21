# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0100_auto_20180919_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventimportattributes',
            name='adm_level_precision',
            field=models.CharField(default=b'1', max_length=10, choices=[(b'1', b'Country'), (b'2', b'Nuts3')]),
        ),
    ]
