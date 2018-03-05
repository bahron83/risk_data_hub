# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0068_event_layers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='layers',
            new_name='related_layers',
        ),
    ]
