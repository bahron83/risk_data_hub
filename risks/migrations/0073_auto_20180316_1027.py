# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0072_auto_20180315_1748'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisClass',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=30, db_index=True)),
                ('title', models.CharField(max_length=80)),
            ],
        ),
        migrations.RemoveField(
            model_name='analysistype',
            name='analysis_class',
        ),
    ]
