# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0079_remove_riskanalysis_matching_ra'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskanalysis',
            name='show_in_event_details',
            field=models.BooleanField(default=False),
        ),
    ]
