# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('risks', '0089_auto_20180712_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='furtherresource',
            name='owner',
            field=models.ForeignKey(related_name='risks_furtherresource', verbose_name=b'Owner', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
