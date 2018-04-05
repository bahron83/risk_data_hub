# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0076_eventimportattributes_allow_null_values'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventimportattributes',
            name='allow_null_values',
            field=models.BooleanField(default=False),
        ),
    ]
