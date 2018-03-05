# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import risks.models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0048_riskanalysisdymensioninfoassociation_scenraio_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('event_id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('iso2', models.CharField(max_length=10)),
                ('begin_date', models.CharField(max_length=10)),
                ('end_date', models.CharField(max_length=10)),
                ('loss_currency', models.CharField(max_length=3)),
                ('loss_amount', models.DecimalField(max_digits=20, decimal_places=6)),
                ('year', models.IntegerField()),
                ('loss_mln', models.DecimalField(max_digits=20, decimal_places=6)),
                ('event_type', models.CharField(max_length=50)),
                ('event_source', models.CharField(max_length=255)),
                ('area_affected', models.DecimalField(max_digits=20, decimal_places=6)),
                ('fatalities', models.IntegerField()),
                ('people_affected', models.IntegerField()),
                ('cause', models.CharField(max_length=100)),
                ('notes', models.CharField(max_length=255)),
                ('sources', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['iso2'],
                'db_table': 'risks_event',
            },
            bases=(risks.models.RiskAppAware, risks.models.LocationAware, risks.models.Exportable, models.Model),
        ),
        migrations.CreateModel(
            name='EventAdministrativeDivisionAssociation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventRiskAnalysisAssociation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event', models.ForeignKey(to='risks.Event')),
            ],
        ),
        migrations.AlterField(
            model_name='administrativedivision',
            name='level',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='riskanalysis',
            name='name',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='riskapp',
            name='name',
            field=models.CharField(unique=True, max_length=64, choices=[(b'data_extraction', b'Data Extraction'), (b'cost_benefit_analysis', b'Cost Benefit Analysis'), (b'test', b'Test')]),
        ),
        migrations.AddField(
            model_name='eventriskanalysisassociation',
            name='ra',
            field=models.ForeignKey(to='risks.RiskAnalysis'),
        ),
        migrations.AddField(
            model_name='eventadministrativedivisionassociation',
            name='adm',
            field=models.ForeignKey(to='risks.AdministrativeDivision'),
        ),
        migrations.AddField(
            model_name='eventadministrativedivisionassociation',
            name='event',
            field=models.ForeignKey(to='risks.Event'),
        ),
        migrations.AddField(
            model_name='event',
            name='administrative_divisions',
            field=models.ManyToManyField(to='risks.AdministrativeDivision', through='risks.EventAdministrativeDivisionAssociation'),
        ),
        migrations.AddField(
            model_name='event',
            name='risk_analysis',
            field=models.ManyToManyField(to='risks.RiskAnalysis', through='risks.EventRiskAnalysisAssociation'),
        ),
    ]
