# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0088_auto_20180712_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='region',
            field=models.ForeignKey(related_name='events', to='risks.Region'),
        ),
    ]
