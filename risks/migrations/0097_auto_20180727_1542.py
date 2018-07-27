# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import risks.customs.custom_storage


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0096_auto_20180719_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventimportattributes',
            name='data_file',
            field=models.FileField(storage=risks.customs.custom_storage.ReplacingFileStorage(), max_length=255, upload_to=b'data_files'),
        ),
        migrations.AlterField(
            model_name='eventimportdata',
            name='data_file',
            field=models.FileField(storage=risks.customs.custom_storage.ReplacingFileStorage(), max_length=255, upload_to=b'data_files'),
        ),
        migrations.AlterField(
            model_name='riskanalysis',
            name='data_file',
            field=models.FileField(max_length=255, upload_to=b'data_files'),
        ),
        migrations.AlterField(
            model_name='riskanalysisimportdata',
            name='data_file',
            field=models.FileField(storage=risks.customs.custom_storage.ReplacingFileStorage(), max_length=255, upload_to=b'data_files'),
        ),
        migrations.AlterField(
            model_name='riskanalysisimportmetadata',
            name='metadata_file',
            field=models.FileField(storage=risks.customs.custom_storage.ReplacingFileStorage(), max_length=255, upload_to=b'metadata_files'),
        ),
    ]
