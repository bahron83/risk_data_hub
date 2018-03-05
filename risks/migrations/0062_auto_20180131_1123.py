# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0061_auto_20180131_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='cause',
            field=models.CharField(max_length=255),
        ),
    ]
