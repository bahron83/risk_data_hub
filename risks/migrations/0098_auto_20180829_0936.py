# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0097_auto_20180727_1542'),
    ]

    operations = [
        migrations.CreateModel(
            name='SendaiTarget',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=10, db_index=True)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='riskanalysisdymensioninfoassociation',
            name='sendai_target',
            field=models.ForeignKey(blank=True, to='risks.SendaiTarget', null=True),
        ),
    ]
