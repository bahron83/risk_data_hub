# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import risks.models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0084_auto_20180626_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='region',
            field=models.ForeignKey(default=risks.models.get_default_region, to='risks.Region'),
        ),
    ]
