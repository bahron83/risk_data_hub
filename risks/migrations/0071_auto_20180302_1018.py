# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0070_auto_20180212_0317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrativedivision',
            name='name',
            field=models.CharField(max_length=555550, db_index=True),
        ),
    ]
