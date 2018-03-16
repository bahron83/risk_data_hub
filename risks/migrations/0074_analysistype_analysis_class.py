# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0073_auto_20180316_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysistype',
            name='analysis_class',
            field=models.ForeignKey(to='risks.AnalysisClass', null=True),
        ),
    ]
