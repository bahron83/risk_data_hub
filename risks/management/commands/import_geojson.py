import traceback
import psycopg2
import os
import ijson
from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis import geos
from action_utils import DbUtils


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--commit',
            action='store_true',
            dest='commit',
            default=True,
            help='Commits Changes to the storage.')
        return parser

    def handle(self, **options):
        commit = options.get('commit')
        db = DbUtils()
        conn = db.get_db_conn()
        basedir = "/home/geonode/import_data/polygons/events"
        allowed_extensions = [".json", ".geojson"]
        
        try:
            for file in os.listdir(basedir):
                if file.endswith(tuple(allowed_extensions)):
                    with open(os.path.join(basedir, file), "r") as f:
                        #filedata = f.read()                        
                        #filedata = filedata.replace('"rings"', '"type": "Polygon","coordinates"')
                        parser = ijson.parse(f)
                        geometry = None
                        event_id = None
                        for prefix, event, value in parser:                               
                            if (prefix, event) == ('features.item', 'start_map'):
                                event_id = None
                                geometry = None
                            elif prefix == 'features.item.properties.EVENT_ID':
                                event_id = value                                
                            elif prefix.startswith('features.item.geometry'):
                                string_value = ''
                                if event == 'start_map':
                                    string_value = '{'
                                elif event == 'map_key':
                                    string_value = '"%s": ' % value
                                elif event == 'string':
                                    string_value = '"%s",' % value
                                elif event == 'start_array':
                                    string_value = '['
                                elif event == 'end_array':
                                    string_value = '],'
                                elif event == 'number':
                                    string_value = '%s,' % value
                                elif event == 'end_map':
                                    string_value = '}'
                                geometry = string_value if geometry is None else geometry + string_value
                            elif (prefix, event) == ('features.item', 'end_map'):
                                #print event_id
                                #print str(geometry).replace(',]', ']').replace(',}', '}')
                                print 'Inserting Event {}'.format(event_id)
                                values = { 'event_id': event_id, 'geometry': str(geometry).replace(',]', ']').replace(',}', '}') }
                                self.insert_data(conn, values)                                                            
                        os.rename(os.path.join(basedir, file), '{}/archive/{}'.format(basedir, file))


            conn.commit()

        except Exception:
            try:
                conn.rollback()
            except:
                pass

            traceback.print_exc()
        finally:
            conn.close()

    def insert_data(self, conn, values):        
        curs = conn.cursor()
        '''insert_template = """WITH data AS (SELECT '{geo_json}'::json AS fc)
                            INSERT INTO events (the_geom, event_id)
                            SELECT                        
                                ST_SetSRID(ST_Multi(ST_GeomFromGeoJSON(feat->>'geometry')), 4326) AS the_geom,
                                replace(cast((feat->'properties')->'EventID' as text), '"', '') as event_id
                            FROM (
                                SELECT json_array_elements(fc->'features') AS feat
                                FROM data
                            ) AS f
                            ON CONFLICT (event_id) DO UPDATE SET the_geom = excluded.the_geom;"""
                            '''
        insert_template = """INSERT INTO events (the_geom, event_id)
                            SELECT                        
                                ST_SetSRID(ST_Multi(ST_GeomFromGeoJSON('{geometry}')), 4326) AS the_geom,
                                replace(cast('{event_id}' as text), '"', '') as event_id                            
                            ON CONFLICT (event_id) DO UPDATE SET the_geom = excluded.the_geom;"""

        curs.execute(insert_template.format(**values))