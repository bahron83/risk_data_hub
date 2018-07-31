# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.gdal import DataSource
from django.contrib.gis import geos
from mptt.managers import TreeManager

from risks.models import Region, AdministrativeDivision, RegionAdministrativeDivisionAssociation 


class Command(BaseCommand):
    """
    Example Usage:
    $> python manage.py populateau -a 0 -r Afghanistan -l 3 \
         -s i_AdminBoundaries_AGCHO/afg_admbnd_adm0_pol.shp
    $> python manage.py populateau -a 1 -r Afghanistan -l 3 \
         -s i_AdminBoundaries_AGCHO/afg_admbnd_adm1_pol.shp
    $> python manage.py populateau -a 2 -r Afghanistan -l 3 \
         -s i_AdminBoundaries_AGCHO/afg_admbnd_adm2_pol.shp
    """

    help = 'Populate Administrative Units Dataset'

    option_list = BaseCommand.option_list + (
        make_option(
            '-a',
            '--adm-level',
            dest='adm_level',
            type="int",
            help='Administrative Unit Level.'),
        make_option(
            '-r',
            '--region',
            dest='region',
            type="string",
            help='Destination Region.'),
        make_option(
            '-l',
            '--region-level',
            dest='region_level',
            type="int",
            help='Region Level: {0 is global; 1 is continent; \
2 is sub-continent; 3 is country}'),
        make_option(
            '-s',
            '--shape-file',
            dest='shape_file',
            type="string",
            help='Input Administrative Unit Shapefile.'),
        make_option(
            '-t',
            '--tolerance',
            dest='tolerance',
            type="float",
            default=0.0001,
            help='Geometry Simplify Tolerance. [0.0001]'))

    def handle(self, **options):
        adm_level = options.get('adm_level')
        region = options.get('region')
        region_level = options.get('region_level')
        shape_file = options.get('shape_file')
        tolerance = options.get('tolerance')

        if adm_level is None:
            raise CommandError("Input Administrative Unit Level '--adm-level' \
is mandatory")

        if region is None:
            raise CommandError("Input Destination Region '--region' \
is mandatory")

        if region_level is None:
            raise CommandError("Input Region Level '--region-level' \
is mandatory")

        if not shape_file or len(shape_file) == 0:
            raise CommandError("Input Administrative Unit Shapefile \
'--shape-file' is mandatory")

        ds = DataSource(shape_file)
        print('Opening Data Source "%s"' % ds.name)

        #print('rebuilding tree')
        #AdministrativeDivision.objects.rebuild()
        #print('rebuilding complete!')                                            

        for layer in ds:
            print('Layer "%s": %i %ss' %
                  (layer.name, len(layer), layer.geom_type.name))

            (region_obj, is_new_region) = Region.objects.get_or_create(
                name=region,
                defaults=dict(
                    level=region_level
                )
            )

            adm_rows = []          
            
            
             
            for feat in layer:
                # Simplify the Geometry
                geom = geos.fromstr(feat.geom.wkt, srid=4326)                
                if tolerance > 0:                    
                    geom = geom.simplify(tolerance, preserve_topology=True)

                # Generalize to 'Multiploygon'                
                if isinstance(geom, geos.Polygon):
                    geom = geos.MultiPolygon(geom)

                if adm_level == 0:
                    (adm_division, is_new_amdiv) = \
                        AdministrativeDivision.objects.get_or_create(
                            code=feat.get('HRPcode'),
                            defaults=dict(
                                name=feat.get('HRname'),
                                geom=geom.wkt                                
                            )
                        )                    

                    if not is_new_amdiv:
                        adm_division.name = feat.get('HRname')
                        adm_division.geom = geom.wkt                        
                        adm_division.save()
                    else:
                        #region_obj.administrative_divisions.add(adm_division)
                        RegionAdministrativeDivisionAssociation.objects.create(region=region_obj, administrativedivision=adm_division)                        

                if adm_level == 1:                                        
                    adm_division_0 = \
                        AdministrativeDivision.objects.get(
                            code=feat.get('HRparent'))
                    (adm_division, is_new_amdiv) = \
                        AdministrativeDivision.objects.get_or_create(
                            code=feat.get('HRpcode'),
                            defaults=dict(
                                name=feat.get('HRname'),
                                geom=geom.wkt,                                
                                parent=adm_division_0
                            )
                        )

                    if not is_new_amdiv:
                        adm_division.name = feat.get('HRname')
                        adm_division.geom = geom.wkt                        
                        adm_division.parent = adm_division_0
                        adm_division.save()
                    else:
                        #region_obj.administrative_divisions.add(adm_division)                        
                        RegionAdministrativeDivisionAssociation.objects.create(region=region_obj, administrativedivision=adm_division)                        

                if adm_level == 2:
                    print('region = {}'.format(feat.get('HRpcode')))
                    adm_division_1 = AdministrativeDivision.objects.get(code=feat.get('HRparent'))
                    (adm_division, is_new_amdiv) = AdministrativeDivision.objects.get_or_create(
                        code=feat.get('HRpcode'),
                        defaults=dict(
                            name=feat.get('HRname'),
                            geom=geom.wkt,                            
                            parent=adm_division_1
                        )
                    )

                    if not is_new_amdiv:
                        adm_division.name = feat.get('HRname')
                        adm_division.geom = geom.wkt                        
                        adm_division.parent = adm_division_1
                        adm_division.save()
                    else:
                        #region_obj.administrative_divisions.add(adm_division)                        
                        RegionAdministrativeDivisionAssociation.objects.create(region=region_obj, administrativedivision=adm_division)                        
                
                if adm_level == 3:
                    
                    
                     
                    print('adm = {}'.format(feat.get('HRpcode')))
                    print('parent = {}'.format(feat.get('HRparent')))
                    adm_division_2 = AdministrativeDivision.objects.get(code=feat.get('HRparent'))
                    '''(adm_division, is_new_amdiv) = AdministrativeDivision.objects.get_or_create(
                        code=feat.get('HRpcode'),
                        defaults=dict(
                            name=feat.get('HRname'),
                            geom=geom.wkt,
                            region=region_obj,
                            parent=adm_division_2
                        )
                    )
                    
                    if not is_new_amdiv:
                        adm_division.name = feat.get('HRname')
                        adm_division.geom = geom.wkt
                        adm_division.region = region_obj
                        adm_division.parent = adm_division_2
                        adm_division.save()
                    else:
                        region_obj.administrative_divisions.add(adm_division)'''

                    
                                        
                    lookup_obj = AdministrativeDivision.objects.filter(code=feat.get('HRpcode'))
                    if lookup_obj.exists():
                        adm_division = AdministrativeDivision.objects.get(code=feat.get('HRpcode'))
                        adm_division.name = feat.get('HRname')
                        adm_division.geom = geom.wkt                        
                        adm_division.parent = adm_division_2
                        adm_division.save()
                        association, created = RegionAdministrativeDivisionAssociation.objects.get_or_create(region=region_obj, administrativedivision=adm_division)                        
                        print('updated object {}'.format(feat.get('HRpcode')))
                    else:
                        adm_division = AdministrativeDivision(
                            code=feat.get('HRpcode'),
                            name=feat.get('HRname'),
                            geom=geom.wkt,                            
                            level=adm_level,
                            parent=adm_division_2,
                            lft=1,
                            rght=1,
                            tree_id=1,
                        )                        
                        adm_rows.append(adm_division)

                        if(len(adm_rows) > 9999):
                            print('bulk insert starting')
                            AdministrativeDivision.objects.bulk_create(adm_rows)
                            for adm_code in adm_rows:
                                adm_div = AdministrativeDivision.objects.get(code=adm_code)
                                RegionAdministrativeDivisionAssociation.objects.create(region=region_obj, administrativedivision=adm_div)                        
                            print('bulk insert complete')
                            adm_rows[:] = []

            
            #print(adm_rows.count())
            if(len(adm_rows) > 0):                                
                print('bulk insert starting')
                AdministrativeDivision.objects.bulk_create(adm_rows)
                for adm_code in adm_rows:
                    adm_div = AdministrativeDivision.objects.get(code=adm_code)
                    RegionAdministrativeDivisionAssociation.objects.create(region=region_obj, administrativedivision=adm_div)                        
                print('bulk insert complete')
                # region_obj.administrative_divisions.add(*adm_rows)
                #print('rebuilding tree')
                #AdministrativeDivision.objects.rebuild()
                #print('rebuilding complete!')                                            
