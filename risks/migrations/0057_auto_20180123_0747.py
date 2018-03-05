# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0056_auto_20180123_0502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='area_affected',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=6),
        ),
        migrations.AlterField(
            model_name='event',
            name='loss_amount',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=6),
        ),
        migrations.AlterField(
            model_name='event',
            name='loss_mln',
            field=models.DecimalField(null=True, max_digits=20, decimal_places=6),
        ),
    ]
