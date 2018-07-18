# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0093_administrativedivisionmappings'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativedivisionmappings',
            name='name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
