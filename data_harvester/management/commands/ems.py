from django.core.management.base import BaseCommand
import os
import get_ems_zips
import merge_ems_zips
import get_ems_pics
import ems_feed_reader
import csv
from django.conf import settings
from risks.management.commands.action_utils import DbUtils
import json


###############################################################################
# CONFIGURATION
# configure the EMS tags that you want as ZIP vector data in first row of conf.csv
# example configure EMSR238 -> emergency_tags=["EMSR238"]
# configure the EMS tags elements that you want to extract as data in second row of conf.csv
# example configure observed_event_a- > elements = ['observed_event_a']
# configure the EMS pics properties in terms of format and resolution that you want to extract as data in third row of conf.csv
# example configure pdf; 300 -> pics_conf = ['pdf', '300'] where first is image extension (pdf, jpg or tif) and second is the resolution (100, 200 or 300)
###############################################################################
def configure(filename):
    ifile = open(filename, "rU")
    reader = csv.reader(ifile, delimiter=";")
    rownum = 0
    a = []
    for row in reader:
        a.append (row)
        rownum += 1
    ifile.close()
    return a

class Command(BaseCommand):
    def handle(self, **options):

        #configure
        conf=configure(os.path.join(settings.LOCAL_ROOT, '../data_harvester/management/commands/conf.csv'))
        #emergency_tags=conf[0]
        #elements=conf[1]
        #pics_conf=conf[2]        

        elements = ['observed_event_a']

        #look for updates from feed
        print('start parsing feed...')
        data_from_feed = ems_feed_reader.parse_feed('rapid')
        #with open('/home/geo/data_from_feed.json', 'w') as f:
        #    f.write(json.dumps(data_from_feed))
        
        print('resolves events to import...')
        emergency_tags = ems_feed_reader.get_ems_to_import('rapid', data_from_feed)

        #download data
        print('start downloading zip files...')
        get_ems_zips.get_ems_zips(emergency_tags)

        #download pics
        #get_ems_pics.get_ems_pics(emergency_tags, pics_conf)

        #merging shapefiles
        print('start merging zip files...')
        merge_ems_zips.merge_ems_zips(emergency_tags,elements)

        #update events with geometry
        print('import events in database...')
        ems_feed_reader.import_events(data_from_feed)

        #set emergency tags as imported
        print('update flows...')
        ems_feed_reader.set_tags_imported(emergency_tags)




