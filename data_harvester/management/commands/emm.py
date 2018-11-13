import os
import traceback
import ijson
import datetime
from dateutil.parser import parse
from django.contrib.gis import geos
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from risks.models import (Event, HazardType, AdministrativeDivision, Region, 
                            EventAdministrativeDivisionAssociation, RiskAnalysis, DataProviderMappings)
from risks.helpers import EventHelper
from risks.management.commands.action_utils import DbUtils


class Command(BaseCommand):
    
    def get_adm_from_coordinates(self, coordinates, parent):        
        point = geos.Point(coordinates['lon'], coordinates['lat'], srid=4326)
        adm_divisions = AdministrativeDivision.objects.filter(parent=parent)
        for adm in adm_divisions:
            adm_geom = geos.fromstr(adm.geom, srid=4326)
            if point.intersects(adm_geom):
                return adm
    
    def resolve_hazard_type(self, term):
        mappings = {
            'LS': 'LS',
            'EQ': 'EQ',
            'FL': 'FL',
            'WF': 'FF',
            'VO': 'VO',
            'AV': 'AV',
            'HE': 'HE'
        }
        if term in mappings:
            return HazardType.objects.filter(mnemonic=mappings[term]).first()

    def handle(self, **options):        
        db = DbUtils()
        conn = db.get_db_conn()
        basedir = "/home/geonode/import_data/emm"
        allowed_extensions = [".json", ".geojson"]
        default_region = Region.objects.get(name='Europe')
        default_adm_region = AdministrativeDivision.objects.get(code='EU')
        eh = EventHelper()
        data_provider_mappings = DataProviderMappings.objects.filter(data_provider__name='EMM')      
        
        try:
            for file in os.listdir(basedir):
                if file.endswith(tuple(allowed_extensions)):
                    print 'opening file {}'.format(file)
                    with open(os.path.join(basedir, file), "r") as f:                        
                        parser = ijson.parse(f) 
                        event_obj = {}                                               
                        data_attributes = []
                        index = 0                        
                        for prefix, event, value in parser:                                                         
                            if data_provider_mappings:
                                for m in data_provider_mappings:                                        
                                    if prefix.endswith(m.provider_value) and 'hazard_type' in event_obj:
                                        #print 'reading property {}'.format(prefix)
                                        #print 'event obj {}'.format(event_obj)
                                        index = len(data_attributes)-1
                                        data_attributes[index]['dim1'] = m.rdh_value
                                        data_attributes[index][m.rdh_value] = value                                        
                                        data_attributes[index]['risk_analysis'] = m.get_risk_analysis(default_region, event_obj['hazard_type'])
                            if (prefix, event) == ('data.item', 'start_map'):
                                print 'start map data'
                                country = None
                                event_obj = {}                                
                                data_attributes.append({})                                
                            elif prefix.endswith('description'):
                                event_obj['notes'] = value
                            elif prefix.endswith('pubDate'):                                
                                try:
                                    begin_date = parse(value)
                                    end_date = begin_date
                                    year = begin_date.year
                                except:
                                    year = value[:4]
                                    begin_date = datetime.datetime(year, 1, 1)
                                    end_date = begin_date
                                event_obj['begin_date'] = begin_date
                                event_obj['end_date'] = end_date
                                event_obj['year'] = year
                            elif prefix.endswith('type'):
                                resolved_hazard = self.resolve_hazard_type(value)
                                if resolved_hazard:
                                    event_obj['hazard_type'] = resolved_hazard
                                else:
                                    continue                                
                            elif prefix.endswith('locationLat'):
                                event_obj['lat'] = value
                            elif prefix.endswith('locationLon'):
                                event_obj['lon'] = value                                                           
                            elif (prefix, event) == ('data.item', 'end_map'):                                
                                if 'hazard_type' in event_obj: 
                                    #print 'event_obj {}'.format(event_obj)
                                    event_obj['region'] = default_region
                                    if 'lat' in event_obj and 'lon' in event_obj:
                                        coordinates = {'lon': float(event_obj['lon']), 'lat': float(event_obj['lat'])}
                                        country_from_intersection = self.get_adm_from_coordinates(coordinates, default_adm_region) 
                                        if not country_from_intersection:
                                            data_attributes.pop()                                                                                       
                                            continue
                                        data_attributes[index]['adm_div'] = country_from_intersection
                                        event_obj['iso2'] = country_from_intersection.code                                    
                                        nuts_from_intersection = self.get_adm_from_coordinates(coordinates, country_from_intersection)    
                                        if nuts_from_intersection:
                                            event_obj['nuts3'] = nuts_from_intersection.code
                                            data_attributes[index]['adm_div'] = nuts_from_intersection
                                        del event_obj['lat']
                                        del event_obj['lon']
                                    duplicates = Event.find_matches(event_obj)
                                    if not duplicates:
                                        #event_obj['event_id'] = Event.generate_event_id(event_obj['hazard_type'], event_obj['iso2'], event_obj['begin_date'], default_region)                                                                            
                                        event_obj['sources'] = 'EMM'
                                        event_obj['cause'] = ''
                                        event_obj['state'] = 'draft'
                                        event = Event(**event_obj)
                                        print 'saving event object'                                        
                                        event.save() 
                                        event.refresh_from_db()                                          
                                        print event
                                        eh.set_event(event)                                        
                                        eh.set_adm_associations()
                                        #insert event into Geoserver DB                                        
                                        event_obj['event_id'] = event.id
                                        db.insert_event(conn, event_obj)
                                        #insert risk analysis values into Geoserver DB                                        
                                        if data_attributes:                                            
                                            data_attributes[index]['event'] = event
                                    else:
                                        data_attributes.pop()
                                else:
                                    data_attributes.pop()
                        os.rename(os.path.join(basedir, file), '{}/archive/{}'.format(basedir, file))

                        print 'saving event attributes'  
                        print data_attributes                      
                        eh.insert_event_attributes(data_attributes, conn)

            conn.commit()

        except Exception:
            try:
                conn.rollback()
            except:
                pass

            traceback.print_exc()
        finally:
            conn.close()
