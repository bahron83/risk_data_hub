# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0090_furtherresource_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativedata',
            name='indicator_type',
            field=models.CharField(default='area', max_length=50),
            preserve_default=False,
        ),
    ]
