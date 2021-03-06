# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0054_hazardtype_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='state',
            field=models.CharField(default=b'ready', max_length=64, choices=[(b'queued', b'Queued'), (b'processing', b'Processing'), (b'ready', b'Ready'), (b'error', b'Error')]),
        ),
    ]
