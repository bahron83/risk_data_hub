# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0106_auto_20181107_1609'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='event_id',
            new_name='code',
        ),
    ]
