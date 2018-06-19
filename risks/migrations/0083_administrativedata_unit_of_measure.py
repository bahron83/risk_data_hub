# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0082_auto_20180618_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativedata',
            name='unit_of_measure',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
    ]
