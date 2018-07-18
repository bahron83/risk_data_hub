# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0092_riskanalysis_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrativeDivisionMappings',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=50)),
                ('child', models.ForeignKey(related_name='mapping_parent', to='risks.AdministrativeDivision')),
                ('parent', models.ForeignKey(related_name='mapping_child', to='risks.AdministrativeDivision')),
            ],
        ),
    ]
