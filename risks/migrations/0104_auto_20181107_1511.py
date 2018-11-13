# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risks', '0103_auto_20181030_1532'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dataprovidermappings',
            options={'verbose_name': 'DataProviderMappings', 'verbose_name_plural': 'DataProviderMappings'},
        ),
        migrations.AddField(
            model_name='event',
            name='id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='dataprovidermappings',
            name='rdh_value',
            field=models.CharField(max_length=80, choices=[(b'10', b'10'), (b'area_flooded', b'area_flooded'), (b'Buildup_potential_impact', b'Buildup_potential_impact'), (b'burned_area', b'burned_area'), (b'Economic_losses', b'Economic_losses'), (b'Event_value', b'Event_value'), (b'fatalities', b'fatalities'), (b'Habitats_potential_impact', b'Habitats_potential_impact'), (b'Light', b'Light'), (b'Low Susceptibility', b'Low Susceptibility'), (b'Marine Habitats', b'Marine Habitats'), (b'people_affected', b'people_affected'), (b'Potential_impact', b'Potential_impact'), (b'total', b'total'), (b'Total', b'Total'), (b'50', b'50'), (b'City_centre', b'City_centre'), (b'City_Centre', b'City_Centre'), (b'Coastal Habitats', b'Coastal Habitats'), (b'Moderate', b'Moderate'), (b'Moderate Susceptibility', b'Moderate Susceptibility'), (b'100', b'100'), (b'#100', b'#100'), (b'Heavy', b'Heavy'), (b'High Susceptibility', b'High Susceptibility'), (b'Urban', b'Urban'), (b'200', b'200'), (b'#200', b'#200'), (b'Rural', b'Rural'), (b'Very high Susceptibility', b'Very high Susceptibility'), (b'500', b'500'), (b'#500', b'#500')]),
        ),
    ]
