import traceback
import psycopg2

from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from risks.models import Region, AdministrativeDivision, Event, AdministrativeDivisionMappings
from risks.models import HazardType, RiskApp
from risks.models import RiskAnalysisDymensionInfoAssociation
from risks.models import RiskAnalysisAdministrativeDivisionAssociation
from risks.models import EventAdministrativeDivisionAssociation, EventFurtherAdministrativeDivisionAssociation
from action_utils import DbUtils

import xlrd
from xlrd.sheet import ctype_text

from dateutil.parser import parse
import datetime
import time
import re


def is_int(string):
    try:
        n = int(string)
        return True
    except ValueError, e:
        return False

class Command(BaseCommand):
    help = 'Import Risk Data: Loss Impact and Impact Analysis Types.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--commit',
            action='store_true',
            dest='commit',
            default=True,
            help='Commits Changes to the storage.')
        parser.add_argument(
            '-r',
            '--region',
            dest='region',
            type=str,
            help='Destination Region.')
        parser.add_argument(
            '-x',
            '--excel-file',
            dest='excel_file',
            type=str,
            help='Input Risk Data Table as XLSX File.')                
        parser.add_argument(
            '-a',
            '--risk-app',
            dest='risk_app',
            type=str,            
            default=RiskApp.APP_DATA_EXTRACTION,
            help="Name of Risk App, default: {}".format(RiskApp.APP_DATA_EXTRACTION),
            )
        return parser    

    
    def handle(self, **options):
        commit = options.get('commit')
        region = options.get('region')
        excel_file = options.get('excel_file')        
        #hazard_type = options.get('hazard_type')        
        risk_app =  options.get('risk_app')
        app = RiskApp.objects.get(name=risk_app)

        if region is None:
            raise CommandError("Input Destination Region '--region' is mandatory")

        #if hazard_type is None:
            #raise CommandError("Input Hazard Type associated to the File '--hazard_type' is mandatory")

        if not excel_file or len(excel_file) == 0:
            raise CommandError("Input Risk Data Table '--excel_file' is mandatory")

        #hazard = HazardType.objects.get(mnemonic=hazard_type)

        wb = xlrd.open_workbook(filename=excel_file)
        region = Region.objects.get(name=region)
        event_ids = []

        sheet = wb.sheet_by_index(0)
        row_headers = sheet.row(0)        

        col_num = 0
        n_events = 0
        for idx, cell_obj in enumerate(row_headers):
            col_num += 1
        if col_num >= 0:

            db = DbUtils()
            conn = db.get_db_conn()        
            try:  
                for row_num in range(1, sheet.nrows):  
                    obj = {}                
                    event_id = str(sheet.cell(row_num, 0).value).replace('\n', '').replace('\r', '').strip()  
                    duplicates = []                                  
                    
                    obj['hazard_type'] = HazardType.objects.get(mnemonic=sheet.cell(row_num, 1).value)
                    obj['region'] = region
                    obj['iso2'] = str(sheet.cell(row_num, 2).value).strip()
                    obj['nuts3'] = str(sheet.cell(row_num, 3).value).replace(' ', '')
                    obj['year'] = int(sheet.cell(row_num, 4).value)                                
                    begin_date_raw = sheet.cell(row_num, 5).value
                    end_date_raw = sheet.cell(row_num, 6).value
                    obj['event_type'] = sheet.cell(row_num, 7).value
                    obj['event_source'] = sheet.cell(row_num, 8).value                
                    obj['cause'] = sheet.cell(row_num, 9).value
                    obj['notes'] = sheet.cell(row_num, 10).value
                    obj['sources'] = sheet.cell(row_num, 11).value                     

                    try:
                        country = AdministrativeDivision.objects.get(code=obj['iso2'], level=1)
                    except AdministrativeDivision.DoesNotExist:                        
                        raise CommandError("Could not find adm unit with code {}".format(obj['iso2']))

                    obj['begin_date'] = datetime.date(obj['year'], 1, 1)
                    obj['end_date'] = datetime.date(obj['year'], 1, 1)              
                    if is_number(begin_date_raw) and is_number(begin_date_raw):                    
                        try:
                            obj['begin_date'] = xlrd.xldate_as_datetime(begin_date_raw, 0)
                            obj['end_date'] = xlrd.xldate_as_datetime(end_date_raw, 0)
                        except:
                            pass
                    else:
                        try:
                            obj['begin_date'] = parse(begin_date_raw)
                            obj['end_date'] = parse(end_date_raw)
                        except ValueError:
                            pass
                    
                    if not event_id:
                        event_id, duplicates = Event.generate_event_id(obj['hazard_type'], country, obj['begin_date'], region)
                        #sheet.put_cell(row_num, 0, xlrd.XL_CELL_TEXT, event_id, sheet.cell_xf_index(row_num, 0))
                                        
                    try:
                        event = Event.objects.get(event_id=event_id, region=region)
                        for key, value in obj.items():
                            setattr(event, key, value)                    
                        event.save()
                    except Event.DoesNotExist:
                        obj['event_id'] = event_id
                        event = Event(**obj)
                        event.save()                                                                               
                    
                    adm_link, created = EventAdministrativeDivisionAssociation.objects.update_or_create(event=event, adm=country)
                    n_events += 1         

                    nuts3_list = event.nuts3.split(';')
                    nuts2_matches = AdministrativeDivisionMappings.objects.filter(child__pk__in=nuts3_list).distinct()
                    if nuts2_matches:
                        for nuts2 in nuts2_matches:
                            EventFurtherAdministrativeDivisionAssociation.objects.update_or_create(event=event, f_adm=nuts2)
                    for adm_code in nuts3_list:                    
                        try:
                            adm_div = AdministrativeDivision.objects.get(regions__id__exact=region.id, code=adm_code)
                            adm_link, created = EventAdministrativeDivisionAssociation.objects.update_or_create(event=event, adm=adm_div)                        
                        except AdministrativeDivision.DoesNotExist:
                            traceback.print_exc()
                            #print(adm_code)
                            pass 

                    #insert into geoserver db
                    obj['event_id'] = event_id
                    db.insert_event(conn, obj)

                    #append event id to return list                        
                    formatted_text_row = '{}\tSuspected duplicate of {}'.format(event_id, ';'.join(duplicates)) if duplicates else event_id
                    event_ids.append(formatted_text_row)
                conn.commit()
            except Exception, e:
                try:
                    conn.rollback()
                except:
                    pass

                #traceback.print_exc()
                raise CommandError(e)
            finally:
                conn.close() 
        return '\r\n'.join(event_ids)
    
def try_parse_int(s, base=10, default=None):
    try:
        return int(s, base)
    except ValueError:
        return default

def try_parse_float(s, default=None):
    try:
        return float(s)
    except ValueError:
        return default

def is_number(s, default=None):
    try:
        res = float(s)
    except ValueError:
        return False
    return True