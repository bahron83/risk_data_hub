from django.core.management.base import BaseCommand
import os
import get_ems_zips
import merge_ems_zips
import get_ems_pics
import ems_feed_reader
import csv
from django.conf import settings
from risks.management.commands.action_utils import DbUtils


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
        conf=configure(os.path.join(settings.BASE_DIR, 'data_harvester/management/commands/conf.csv'))
        emergency_tags=conf[0]
        elements=conf[1]
        pics_conf=conf[2]

        #initialise db connection
        db = DbUtils()
        conn = db.get_db_conn()
        curs = conn.cursor()        

        #look for updates from feed
        data_from_feed = ems_feed_reader.parse_feed(ems_feed_reader.RAPID_MAPPING_URL)        
        emergency_tags_from_feed = [d['copernicus_id'] for d in data_from_feed]        
        ems_string = "', '".join(emergency_tags_from_feed)
        select_template = "SELECT asset_id FROM flows WHERE name = 'ems' AND asset_id IN ('{}')".format(ems_string)
        curs.execute(select_template)
        already_imported = []
        while True:
            row = curs.fetchone()
            if row == None:
                break
            already_imported.append(row)
        emergency_tags = emergency_tags_from_feed - already_imported
        conn.close()

        #download data
        get_ems_zips.get_ems_zips(emergency_tags)

        #download pics
        #get_ems_pics.get_ems_pics(emergency_tags, pics_conf)

        #merging shapefiles
        merge_ems_zips.merge_ems_zips(emergency_tags,elements)

        #set emergency tags as imported
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




