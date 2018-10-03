import traceback
import psycopg2

from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis import geos

from risks.models import Region, AdministrativeDivision, Event, RiskAnalysis
from risks.models import HazardType, RiskApp
from risks.models import RiskAnalysisDymensionInfoAssociation
from risks.models import RiskAnalysisAdministrativeDivisionAssociation
from risks.models import EventAdministrativeDivisionAssociation, EventRiskAnalysisAssociation

import xlrd
from xlrd.sheet import ctype_text

from action_utils import DbUtils


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
            '-k',
            '--risk-analysis',
            dest='risk_analysis',
            type=str,
            help='Name of the Risk Analysis associated to the File.')
        parser.add_argument(
            '-a',
            '--risk-app',
            dest='risk_app',
            type=str,
            # nargs=1,
            default=RiskApp.APP_DATA_EXTRACTION,
            help="Name of Risk App, default: {}".format(RiskApp.APP_DATA_EXTRACTION),
            )
        parser.add_argument(
            '-n',
            '--allow-nulls',
            dest='allow_null_values',            
            default=False,
            help="Allow null values: if no, rows with null values will be skipped",
            )        
        parser.add_argument(
            '-p',
            '--adm-level-precision',
            dest='adm_level_precision', 
            type=str,           
            default='1',
            help="Resolution of data loaded (level of country/nuts3/commune",
            )        
        return parser

    def handle(self, **options):
        commit = options.get('commit')
        region_name = options.get('region')
        excel_file = options.get('excel_file')
        risk_analysis = options.get('risk_analysis')        
        risk_app =  options.get('risk_app')
        allow_null_values = options.get('allow_null_values')     
        adm_level_precision = int(options.get('adm_level_precision'))
        app = RiskApp.objects.get(name=risk_app)

        if region_name is None:
            raise CommandError("Input Destination Region '--region' is mandatory")

        if risk_analysis is None:
            raise CommandError("Input Risk Analysis associated to the File '--risk_analysis' is mandatory")

        if not excel_file or len(excel_file) == 0:
            raise CommandError("Input Risk Data Table '--excel_file' is mandatory")

        risk = RiskAnalysis.objects.get(name=risk_analysis, app=app)

        wb = xlrd.open_workbook(filename=excel_file)
        region = Region.objects.get(name=region_name)        

        axis_x = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk, axis='x')
        axis_y = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk, axis='y')
        
        sheet = wb.sheet_by_index(0)
        row_headers = sheet.row(0)            
        db = DbUtils()
        conn = db.get_db_conn()        
        first_call = True
        event_id = ''
        sample_adm_div = None
                
        try:
            for row_num in range(1, sheet.nrows):                
                event_id = str(sheet.cell(row_num, 0).value).strip()
                adm_code = str(sheet.cell(row_num, 1).value).strip()
                dim1 = str(sheet.cell(row_num, 2).value).strip()
                dim2 = str(sheet.cell(row_num, 3).value).strip()
                attribute_value = str(sheet.cell(row_num, 4).value).strip()
                                                                
                try:
                    event = Event.objects.get(event_id=event_id)                                        
                except Event.DoesNotExist:                        
                    raise CommandError('Incorrect Event ID: {}'.format(event_id))                                          
                
                if (attribute_value or allow_null_values) and any(x.value == dim1 for x in axis_x) and any(y.value == dim2 for y in axis_y):                    
                    x = axis_x.get(value=dim1)
                    y = axis_y.get(value=dim2)                                        
                    try:                        
                        adm_div = AdministrativeDivision.objects.get(code=adm_code)
                        sample_adm_div = adm_div
                    except AdministrativeDivision.DoesNotExist:
                        raise CommandError('Event associated with non existing Administrative unit (code: {})'.format(adm_code))                  
                        
                    params = {
                        'adm_div': adm_div,
                        'event': event,
                        'risk': risk,
                        'region': region,
                        'attribute_value': attribute_value,
                        'x': x,
                        'y': y,
                        'first_call': first_call,
                        'create_django_association': True,                        
                        'conn': conn
                    }
                    self.handle_row(params)
                    event_risk, created = EventRiskAnalysisAssociation.objects.get_or_create(risk=risk, event=event)
                    first_call = False

                    #execute this part only if resolution of data is at country level
                    if adm_level_precision == 1:
                        nuts3_list = event.nuts3.split(';')
                        for nuts3 in nuts3_list:                        
                            try:
                                adm_div = AdministrativeDivision.objects.get(code=nuts3)
                                params['adm_div'] = adm_div                            
                                params['create_django_association'] = True if len(nuts3_list) == 1 else False
                                self.handle_row(params)
                            except AdministrativeDivision.DoesNotExist:
                                traceback.print_exc()
                                pass
                        
            #calculate aggregate values for Region (eg. Europe)
            if sample_adm_div:
                region_adm_div = [adm for adm in sample_adm_div.get_parents_chain() if adm.level == 0]
                if region_adm_div:                    
                    adm_to_process = region_adm_div
                    if adm_level_precision == 2:
                        adm_to_process.append(AdministrativeDivision.objects.filter(parent=region_adm_div[0], level=1))
                    params = { 'adm_to_process': adm_to_process , 'risk_analysis_id': risk.id }
                    db.insert_aggregate_values(conn, params)            
                    risk_adm, created = RiskAnalysisAdministrativeDivisionAssociation.objects.get_or_create(riskanalysis=risk, administrativedivision=region_adm_div[0])
            

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

    
    def handle_row(self, params):                 
        db_values = {
            #'table': table_name,  # From rp.layer
            'the_geom': geos.fromstr(params['adm_div'].geom, srid=params['adm_div'].srid),
            'dim1': params['x'].value,
            'dim1_order': params['x'].order,
            'dim2': params['y'].value,
            'dim2_order': params['y'].order,
            'dim3': None,
            'dim4': None,
            'dim5': None,
            'risk_analysis_id': params['risk'].id,
            'risk_analysis': params['risk'].name,
            'hazard_type': params['risk'].hazard_type.mnemonic,
            'adm_name': params['adm_div'].name.encode('utf-8').replace("'", "''"),
            'adm_code': params['adm_div'].code,
            'region': params['region'].name,
            'adm_level': params['adm_div'].level,
            'parent_adm_code': params['adm_div'].parent.code,
            'event_id': params['event'].event_id,
            'begin_date': params['event'].begin_date,
            'end_date': params['event'].end_date,
            'value': params['attribute_value']
        }
        db = DbUtils()
        db.insert_db(params['conn'], db_values, params['first_call'])
        if params['create_django_association']:
            risk_adm, created = RiskAnalysisAdministrativeDivisionAssociation.objects.get_or_create(riskanalysis=params['risk'], administrativedivision=params['adm_div'])
            #event_adm, created = EventAdministrativeDivisionAssociation.objects.get_or_create(event=params['event'], adm=params['adm_div'])
    