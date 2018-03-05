# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0049_auto_20180122_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativedivision',
            name='event',
            field=models.ManyToManyField(to='risks.Event', through='risks.EventAdministrativeDivisionAssociation'),
        ),
        migrations.AddField(
            model_name='riskanalysis',
            name='event',
            field=models.ManyToManyField(to='risks.Event', through='risks.EventRiskAnalysisAssociation'),
        ),
        migrations.AlterField(
            model_name='event',
            name='administrative_divisions',
            field=models.ManyToManyField(related_name='event_adm', through='risks.EventAdministrativeDivisionAssociation', to='risks.AdministrativeDivision'),
        ),
        migrations.AlterField(
            model_name='event',
            name='risk_analysis',
            field=models.ManyToManyField(related_name='event_ra', through='risks.EventRiskAnalysisAssociation', to='risks.RiskAnalysis'),
        ),
    ]
