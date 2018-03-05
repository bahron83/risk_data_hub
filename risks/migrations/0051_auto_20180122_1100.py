# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0050_auto_20180122_1023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventriskanalysisassociation',
            name='event',
        ),
        migrations.RemoveField(
            model_name='eventriskanalysisassociation',
            name='ra',
        ),
        migrations.RemoveField(
            model_name='event',
            name='risk_analysis',
        ),
        migrations.RemoveField(
            model_name='riskanalysis',
            name='event',
        ),
        migrations.AddField(
            model_name='event',
            name='hazard_type',
            field=models.CharField(default=2, max_length=2),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='EventRiskAnalysisAssociation',
        ),
    ]
