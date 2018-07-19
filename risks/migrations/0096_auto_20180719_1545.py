# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0095_auto_20180718_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrativedivisiondataassociation',
            name='dimension',
            field=models.CharField(max_length=50, db_index=True),
        ),
    ]
