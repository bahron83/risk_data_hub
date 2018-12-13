import os
import ijson
import datetime
from dateutil.parser import parse
from django.contrib.gis import geos
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from risks.models import Event, HazardType, AdministrativeDivision, Region, DataProviderMappings
from risks.helpers import EventHelper


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
                        assessment_values = []
                        index = 0                        
                        for prefix, event, value in parser:                                                         
                            if data_provider_mappings:
                                for m in data_provider_mappings:                                        
                                    if prefix.endswith(m.provider_value) and 'hazard_type' in event_obj:
                                        #print 'reading property {}'.format(prefix)
                                        #print 'event obj {}'.format(event_obj)
                                        index = len(assessment_values)-1
                                        assessment_values[index]['dim1'] = m.rdh_value
                                        assessment_values[index][m.rdh_value] = value                                        
                                        assessment_values[index]['damage_assessment'] = m.get_damage_assessments(default_region, event_obj['hazard_type'])
                            if (prefix, event) == ('data.item', 'start_map'):
                                print 'start map data'
                                country = None
                                event_obj = {}                                
                                assessment_values.append({})                                
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
                                            assessment_values.pop()                                                                                       
                                            continue
                                        assessment_values[index]['adm_div'] = country_from_intersection
                                        event_obj['country'] = country_from_intersection
                                        nuts_from_intersection = self.get_adm_from_coordinates(coordinates, country_from_intersection)    
                                        phenomena_list = []
                                        if nuts_from_intersection:
                                            phenomenon_obj = {
                                                'begin_date': event_obj['begin_date'],
                                                'end_date': event_obj['end_date'],
                                                'administrative_division': nuts_from_intersection
                                            }
                                            phenomena_list.append(phenomenon_obj)
                                            assessment_values[index]['adm_div'] = nuts_from_intersection
                                        del event_obj['lat']
                                        del event_obj['lon']
                                    duplicates = Event.find_matches(event_obj)
                                    if not duplicates:
                                        #event_obj['event_id'] = Event.generate_event_id(event_obj['hazard_type'], event_obj['iso2'], event_obj['begin_date'], default_region)                                                                            
                                        event_obj['sources'] = 'EMM'
                                        event_obj['cause'] = ''
                                        event_obj['state'] = 'draft'
                                        event, phenomena = eh.save_event(event_obj, phenomena_list)                                        
                                        if assessment_values:                                            
                                            assessment_values[index]['phenomenon'] = phenomena[0] #in this case we have only one phenomenon per event
                                            eh.insert_assessment_value()
                                    else:
                                        assessment_values.pop()
                                else:
                                    assessment_values.pop()                        

                        print 'saving assessment_values'  
                        print assessment_values                      
                        eh.insert_assessment_values(assessment_values, conn)            

                        os.rename(os.path.join(basedir, file), '{}/archive/{}'.format(basedir, file))
