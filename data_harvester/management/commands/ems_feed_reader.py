import os
import operator
import urllib2
import feedparser
import re
from datetime import timedelta
import traceback
from dateutil.parser import parse
#from geopy.geocoders import Nominatim
from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis import geos
from django.core.management.base import BaseCommand
from risks.models import AdministrativeDivision, Event, HazardType, Region, EventAdministrativeDivisionAssociation
from risks.management.commands.action_utils import DbUtils
from import_shp import shp2postgis


#geolocator = Nominatim(user_agent="risk_data_hub", timeout=3)
RAPID_MAPPING_URL = 'http://emergency.copernicus.eu/mapping/activations-rapid/feed'
RISK_RECOVERY_URL = 'http://emergency.copernicus.eu/mapping/activations-risk-and-recovery/feed'
SHAPEFILES_BASE_DIR = os.path.join(settings.LOCAL_ROOT, 'downloaded', 'ems')

def parse_feed(feed_type = 'rapid'):
    """
    Parses EMS feed and returns a list of dictionaries
    """
    result = []
    url = ''
    if feed_type == 'rapid':
        url = RAPID_MAPPING_URL
    elif feed_type == 'risk':
        url = RISK_RECOVERY_URL        
    if url:
        if os.getenv('http_proxy'):
            os.environ['NO_PROXY'] = 'emergency.copernicus.eu'
        d = feedparser.parse(url)
        for entry in d.entries:                
            hazard_pattern = r'<b>Type of Event:</b>\s?(.*);'
            country_pattern = r'<b>Affected Country:</b>\s?(.*);'
            date_pattern = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}'
            description_pattern = r'<b>Event Description:</b><br /><p>(.*)</p>'
            
            summary_detail = entry.summary_detail.value
            
            hazard_check = re.findall(hazard_pattern, summary_detail)
            country_check = re.findall(country_pattern, summary_detail)        
            event_check = re.findall(date_pattern, summary_detail)
            description_check = re.findall(description_pattern, summary_detail.replace('\r\n', '').replace('\n', ''))            

            hazard = re.sub(hazard_pattern, r'\1', hazard_check[0]) if hazard_check else None        
            country = re.sub(country_pattern, r'\1', country_check[0]) if country_check else None                
            event_date = event_check[0] if event_check else None
            description = re.sub(description_pattern, r'\1', description_check[0]) if description_check else None

            coordinates = entry.where.coordinates[::-1]
            #location = geolocator.reverse(','.join(str(c) for c in coordinates))
            
            result.append({
                'copernicus_id': entry.id,
                'hazard': hazard,
                'country': country,
                'begin_date': event_date,
                'description': description,
                'link': entry.link#,            
                #'location': location.raw                
            })            
    return result

def get_ems_to_import(feed_type = 'rapid', data_from_feed = None):
    """
    Determine which events are updates and returns list of id to be imported
    """        
    if not data_from_feed:
        data_from_feed = parse_feed(feed_type)
    if data_from_feed:    
        #initialise db connection
        db = DbUtils()
        conn = db.get_db_conn()
        curs = conn.cursor()        
        select_template = "SELECT asset_id FROM flows WHERE name = 'ems'"# AND asset_id IN ('{}')".format(ems_string)
        curs.execute(select_template)
        already_imported = []
        while True:
            row = curs.fetchone()
            if row == None:
                break
            already_imported.append(str(row[0]))    
        conn.close()        
        tags_from_feed = [d['copernicus_id'] for d in data_from_feed]  

        #check if Europe
        countries_needed = AdministrativeDivision.objects.filter(parent__code='EU').values_list('name', flat=True)
        tags_filtered = [d['copernicus_id'] for d in data_from_feed if d['country'] in countries_needed]                   
        return list(set(tags_filtered) - set(already_imported))                       
    return []

def set_tags_imported(emergency_tags):
    """
    Update flows table in Geoserver DB
    """
    #initialise db connection
    db = DbUtils()
    conn = db.get_db_conn()
    curs = conn.cursor()        
    insert_template = """INSERT INTO flows (name, asset_id) VALUES ('ems', '{asset_id}')
                            ON CONFLICT (name, asset_id) DO UPDATE
                            SET timestamp = now();"""
    try:
        for asset_id in emergency_tags:
            parameters = {'asset_id': asset_id}
            curs.execute(insert_template.format(**parameters))
        conn.commit()        
    except Exception, e:
        try:
            conn.rollback()
        except:
            pass
        raise CommandError(e)
    finally:
        conn.close()

def get_hazard_match(name):
    """
    Check for matching hazard type in Django DB, comparing hazard name found in EMS feed
    """
    print('hazard name received = {}'.format(name))
    direct_match = HazardType.objects.filter(title__icontains=name).first()
    if not direct_match:
        repls = ('(', ''), (')', '')
        input_name_parts = reduce(lambda a, kw: a.replace(*kw), repls, name).split(' ')
        scores = {}
        for hazard in HazardType.objects.all():
            scores[hazard] = 0
            for p1 in input_name_parts:
                for p2 in hazard.title.split(' '):
                    if p1.lower() in p2.lower() or p2.lower() in p1.lower():
                        scores[hazard] += 1
        return max(scores.iteritems(), key=operator.itemgetter(1))[0]
    return direct_match

def get_country_match(name):
    """
    Check for matching country in Django DB, comparing country name found in EMS feed
    """
    reg_europe = Region.objects.get(name='Europe')
    return AdministrativeDivision.objects.filter(name__icontains=name, level=1, regions__in=[reg_europe]).first()    

def get_event_by_feed(event):
    """
    Returns event from database, if a match is found by event from feed, otherwise returns None
    """

    hazard_match = get_hazard_match(event['hazard'])
    country_match = get_country_match(event['country'])
    match = None
    if hazard_match and country_match:
        lt_date = parse(event['begin_date']) + timedelta(days=7)
        gt_date = parse(event['begin_date']) - timedelta(days=7)
        match = Event.objects.filter(hazard_type=hazard_match, iso2=country_match.code, begin_date__gt=gt_date, begin_date__lt=lt_date).first()
    return match, hazard_match, country_match    

def event_exists(event):
    """
    Check whether an event already exists, looking by hazard, country and date
    """

    return get_event_by_feed is not None

def get_event_matches(events):
    """
    From a list of events from feed, returns a sub-list of the ones matching existing events in database
    """
    
    matches = []
    for e in list(events):
        if event_exists(e):
            matches.append(e)
    return matches 

def get_adm_units_intersected(event, geom):
    """
    For a given event from feed, returns list of NUTS3 whose geometry has positive intersection with geometry of event
    """
    adm_units_covered = []    
    if event and geom:        
        parent_adm = get_country_match(event['country'])
        if parent_adm:            
            for adm_unit in AdministrativeDivision.objects.filter(parent=parent_adm):                
                adm_geom = geos.fromstr(adm_unit.geom, srid=adm_unit.srid)
                if geom.intersects(adm_geom):                    
                    adm_units_covered.append(adm_unit)                                    
    return list(set(adm_units_covered))

def get_event_from_feed(data_from_feed, ems):
    """
    Extracts single event from parser output
    """
    ems_matches = [e for e in data_from_feed if e['copernicus_id'] == ems]
    return ems_matches[0] if ems_matches else None

def generate_event_from_feed(event, geom):
    """
    Create or update event in Django
    """
    print('looking for event match in database')
    match, hazard_match, country_match = get_event_by_feed(event)
    event_obj = None
    adm_units_intersected = get_adm_units_intersected(event, geom)
    if match:
        print('found existing event: {}'.format(match.event_id))
        nuts3_in_event = match.nuts3.split(';')
        nuts3_intersected = [adm.code for adm in adm_units_intersected]
        nuts3_union = list(set(nuts3_in_event).union(nuts3_intersected))
        params = {
            'nuts3': ';'.join(nuts3_union)
        }        
        if 'EMS' not in match.notes:
            params['notes'] = '{}; {} {}'.format(match.notes, event['copernicus_id'], event['description'])            
        if 'EMS' not in match.sources:
            params['sources'] = '{}; {} {}'.format(match.sources, event['copernicus_id'], event['link'])            
        updated = Event.objects.filter(pk=match.pk).update(**params)        
        event_obj = match
    else:        
        print('event to be created => hazard = {} - country = {}'.format(hazard_match, country_match))
        if hazard_match and country_match:
            region_eu = Region.objects.get(name='Europe') 
            event_id, duplicates = Event.generate_event_id(hazard_match, country_match, parse(event['begin_date']), region_eu)            
            new_event = Event.objects.create(
                event_id=event_id,
                hazard_type=hazard_match,
                region=region_eu,
                iso2=country_match.code,
                nuts3=';'.join([adm.code for adm in adm_units_intersected]),
                begin_date=parse(event['begin_date']),
                end_date=parse(event['begin_date']),
                year=event['begin_date'][:4],
                event_type=event['hazard'],
                event_source='Unknown',
                cause='Unknown',
                notes=event['description'],
                sources='{} {}'.format(event['copernicus_id'], event['link'])
            )         
            event_obj = new_event
    # Set relations
    if event_obj and adm_units_intersected:        
        for adm in adm_units_intersected:
            event_adm, created = EventAdministrativeDivisionAssociation.objects.get_or_create(event=event_obj, adm=adm)

    return event_obj

def compute_union_geometry(files, tolerance = 0.0001):    
    polygon_union = geos.GEOSGeometry('POINT (0 0)', srid=4326)
    count = 0
    print('computing geometry union...')
    for f in files:
        print('file {}'.format(f))
        try:
            ds = DataSource(f)
        except GDALException, e:
            traceback.print_exc()
            break
        for layer in ds:            
            for feat in layer:
                print('processing feature {}'.format(count))
                geom = geos.fromstr(feat.geom.wkt, srid=4326)                                                    
                if tolerance > 0:                    
                    geom = geom.simplify(tolerance, preserve_topology=True)

                # Generalize to 'Multiploygon'                
                if isinstance(geom, geos.Polygon):
                    geom = geos.MultiPolygon(geom)
                
                if count == 0:
                    polygon_union = geom.buffer(0)
                else:
                    polygon_union = polygon_union.union(geom.buffer(0))
                count += 1
    return geos.fromstr(polygon_union.wkt, srid=4326)

def import_events(data_from_feed, tolerance = 0.0001):
    """
    For every shapefile in _merged folder, creates or updates event in Django DB and Geoserver DB. 
    The geometry inserted in Geoserver DB is the union of all features found in layer.
    """
    db = DbUtils()
    conn = db.get_db_conn()
    curs = conn.cursor()
    allowed_extensions = [".shp"]

    try:
        for root, dirs, files in os.walk(SHAPEFILES_BASE_DIR):
            print('shapefiles base dir: {}'.format(SHAPEFILES_BASE_DIR))            
            for d in dirs:
                if d.endswith('_merged'):  

                    print('found merged folder')                     
                    for f in os.listdir(os.path.join(SHAPEFILES_BASE_DIR, d)):                        
                        if f.endswith(tuple(allowed_extensions)):
                            print('found shapefiles: {}'.format(f))

                            '''try:
                                filepath = os.path.join(SHAPEFILES_BASE_DIR, d, f)
                                ds = DataSource(filepath)
                            except GDALException, e:
                                traceback.print_exc()
                                break
                            for layer in ds:
                                count = 0 
                                polygon_union = None   
                                for feat in layer:   
                                    print('processing feature {}'.format(count))                                 
                                    # Simplify the Geometry
                                    geom = geos.fromstr(feat.geom.wkt, srid=4326)                                                    
                                    if tolerance > 0:                    
                                        geom = geom.simplify(tolerance, preserve_topology=True)

                                    # Generalize to 'Multiploygon'                
                                    if isinstance(geom, geos.Polygon):
                                        geom = geos.MultiPolygon(geom)
                                    
                                    if count == 0:
                                        polygon_union = geom.buffer(0)
                                    else:
                                        polygon_union = polygon_union.union(geom.buffer(0))
                                    count += 1                                
                                try:
                                    print('re-extracting geom from union polygon')
                                    polygon_union = geos.fromstr(polygon_union.wkt, srid=4326)
                                except:
                                    break'''                                                        
                            ems = d.split('_')[0]
                            select_template = "SELECT ST_AsText(ST_Union(ARRAY(SELECT ST_Buffer(the_geom, 1e-5) FROM {})))".format(ems)
                            row = None
                            try:
                                curs.execute(select_template)
                                row = curs.fetchone()
                            except:
                                pass   
                            #set default multipolygon
                            ext_coords = ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))  
                            int_coords = ((0.4, 0.4), (0.4, 0.6), (0.6, 0.6), (0.6, 0.4), (0.4, 0.4))                       
                            polygon_union = geos.MultiPolygon(geos.Polygon(ext_coords, int_coords), srid=4326)
                            if row:
                                polygon_union = geos.fromstr(row[0], srid=4326)
                            
                            # Update event in Django
                            event_from_feed = get_event_from_feed(data_from_feed, ems)
                            new_event = generate_event_from_feed(event_from_feed, polygon_union)
                            
                            if new_event:
                                params = { 
                                    'geom': polygon_union,
                                    'event_id': new_event.event_id,
                                    'begin_date': new_event.begin_date,
                                    'end_date': new_event.end_date
                                }
                                update_template = """INSERT INTO events (the_geom, event_id, begin_date, end_date) 
                                                        SELECT 
                                                            '{geom}', '{event_id}', '{begin_date}', '{end_date}'
                                                        ON CONFLICT (event_id)
                                                        DO UPDATE SET the_geom = excluded.the_geom;"""
                                print update_template.format(**params)
                                curs.execute(update_template.format(**params))
                    archive_path = os.path.join(SHAPEFILES_BASE_DIR, d, 'archive')
                    if not os.path.exists(archive_path):
                        os.makedirs(archive_path)
                    for f2 in os.listdir(os.path.join(SHAPEFILES_BASE_DIR, d)):
                        filepath = os.path.join(SHAPEFILES_BASE_DIR, d, f2) 
                        if os.path.isfile(filepath):
                            print('moving file {} to {}'.format(f2, archive_path))
                            os.rename(filepath, os.path.join(archive_path, f2))

        conn.commit()        
    except Exception:
        try:
            conn.rollback()
        except:
            pass

        traceback.print_exc()
    finally:
        conn.close()
