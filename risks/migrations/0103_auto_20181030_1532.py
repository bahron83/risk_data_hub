# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0102_auto_20181015_1351'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'risks_dataprovider',
            },
        ),
        migrations.CreateModel(
            name='DataProviderMappings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rdh_value', models.CharField(max_length=80)),
                ('provider_value', models.CharField(max_length=80)),
                ('data_provider', models.ForeignKey(to='risks.DataProvider')),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='state',
            field=models.CharField(default=b'ready', max_length=64, choices=[(b'queued', b'Queued'), (b'processing', b'Processing'), (b'ready', b'Ready'), (b'error', b'Error'), (b'draft', b'Draft')]),
        ),
        migrations.AlterField(
            model_name='hazardtype',
            name='state',
            field=models.CharField(default=b'ready', max_length=64, choices=[(b'queued', b'Queued'), (b'processing', b'Processing'), (b'ready', b'Ready'), (b'error', b'Error'), (b'draft', b'Draft')]),
        ),
        migrations.AlterField(
            model_name='riskanalysis',
            name='state',
            field=models.CharField(default=b'ready', max_length=64, choices=[(b'queued', b'Queued'), (b'processing', b'Processing'), (b'ready', b'Ready'), (b'error', b'Error'), (b'draft', b'Draft')]),
        ),
    ]
