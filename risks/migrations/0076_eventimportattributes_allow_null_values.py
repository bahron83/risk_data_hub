# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0075_auto_20180316_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventimportattributes',
            name='allow_null_values',
            field=models.BooleanField(default=True),
        ),
    ]
