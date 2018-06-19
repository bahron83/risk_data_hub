# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0081_riskanalysis_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrativeData',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AdministrativeDivisionDataAssociation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('dimension', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=50, null=True, blank=True)),
                ('adm', models.ForeignKey(to='risks.AdministrativeDivision')),
                ('data', models.ForeignKey(to='risks.AdministrativeData')),
            ],
            options={
                'db_table': 'risks_administrativedivisiondataassociation',
            },
        ),
        migrations.AddField(
            model_name='administrativedata',
            name='administrative_divisions',
            field=models.ManyToManyField(to='risks.AdministrativeDivision', through='risks.AdministrativeDivisionDataAssociation'),
        ),
        migrations.AddField(
            model_name='administrativedivision',
            name='administrative_data',
            field=models.ManyToManyField(to='risks.AdministrativeData', through='risks.AdministrativeDivisionDataAssociation'),
        ),
    ]
