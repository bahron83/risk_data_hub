# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0094_administrativedivisionmappings_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrativedivisionmappings',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
