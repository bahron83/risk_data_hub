# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import risks.customs.custom_storage


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0098_auto_20180829_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrativedivisiondataassociation',
            name='adm',
            field=models.ForeignKey(related_name='data_association', to='risks.AdministrativeDivision'),
        ),
        migrations.AlterField(
            model_name='administrativedivisiondataassociation',
            name='data',
            field=models.ForeignKey(related_name='administrativedivision_association', to='risks.AdministrativeData'),
        ),
        migrations.AlterField(
            model_name='event',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='riskanalysiscreate',
            name='descriptor_file',
            field=models.FileField(storage=risks.customs.custom_storage.ReplacingFileStorage(), max_length=255, upload_to=b'descriptor_files'),
        ),
    ]
