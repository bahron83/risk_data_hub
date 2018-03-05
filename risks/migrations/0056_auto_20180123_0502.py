# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0055_event_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventadministrativedivisionassociation',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
        migrations.AlterModelTable(
            name='eventadministrativedivisionassociation',
            table='risks_eventadministrativedivisionassociation',
        ),
    ]
