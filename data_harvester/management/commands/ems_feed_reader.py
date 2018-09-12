from django.core.management.base import BaseCommand
import feedparser
import re
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="risk_data_hub", timeout=3)
RAPID_MAPPING_URL = 'http://emergency.copernicus.eu/mapping/activations-rapid/feed'
RISK_RECOVERY_URL = 'http://emergency.copernicus.eu/mapping/activations-risk-and-recovery/feed'

def parse_feed(url):
    d = feedparser.parse(url)
    result = []
    for entry in d.entries:                
        hazard_pattern = r'<b>Type of Event:</b>\s?(.*);'
        country_pattern = r'<b>Affected Country:</b>\s?(.*);'
        date_pattern = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}'
        description_pattern = r'<b>Event Description:</b><br />(<p>.*</p>)'
        
        hazard_check = re.findall(hazard_pattern, entry.summary_detail.value)
        country_check = re.findall(country_pattern, entry.summary_detail.value)        
        event_check = re.findall(date_pattern, entry.summary_detail.value)
        description_check = re.findall(description_pattern, entry.summary_detail.value)

        hazard = re.sub(hazard_pattern, r'\1', hazard_check[0]) if hazard_check else None        
        country = re.sub(country_pattern, r'\1', country_check[0]) if country_check else None                
        event_date = event_check[0] if event_check else None
        description = re.sub(description_pattern, r'\1', description_check[0]) if description_check else None

        coordinates = entry.where.coordinates[::-1]
        location = geolocator.reverse(','.join(str(c) for c in coordinates))
        
        result.append({
            'copernicus_id': entry.id,
            'hazard': hazard,
            'country': country,
            'begin_date': event_date,
            'description': description,
            'link': entry.link,            
            'location': location.raw
        })
        #break

    return result
        

class Command(BaseCommand):
    help = 'Command description...'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--feed',            
            dest='feed',
            type=str,
            default=None,            
            help='Type of feed')

        return parser

    def handle(self, **options):
        feed = options.get('feed')
        url = RISK_RECOVERY_URL if feed == 'risk' else RAPID_MAPPING_URL
        parsed_events = parse_feed(url)
        print parsed_events