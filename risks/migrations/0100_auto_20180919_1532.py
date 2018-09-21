# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0099_auto_20180919_0849'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventRiskAnalysisAssociation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('event', models.ForeignKey(to='risks.Event')),
                ('risk', models.ForeignKey(to='risks.RiskAnalysis')),
            ],
            options={
                'db_table': 'risks_eventriskanalysisassociation',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='risk_analysis',
            field=models.ManyToManyField(to='risks.RiskAnalysis', through='risks.EventRiskAnalysisAssociation'),
        ),
        migrations.AddField(
            model_name='riskanalysis',
            name='events',
            field=models.ManyToManyField(to='risks.Event', through='risks.EventRiskAnalysisAssociation'),
        ),
    ]
