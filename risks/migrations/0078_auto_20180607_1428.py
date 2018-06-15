# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0077_auto_20180404_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskanalysis',
            name='matching_ra',
            field=models.ForeignKey(related_name='riskanalysis_matching', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='risks.RiskAnalysis', null=True),
        ),
        migrations.AlterField(
            model_name='administrativedivision',
            name='name',
            field=models.CharField(max_length=100, db_index=True),
        ),
    ]
