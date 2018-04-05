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
from risks.models import EventAdministrativeDivisionAssociation

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
        return parser

    def handle(self, **options):
        commit = options.get('commit')
        region = options.get('region')
        excel_file = options.get('excel_file')
        risk_analysis = options.get('risk_analysis')        
        risk_app =  options.get('risk_app')
        allow_null_values = options.get('allow_null_values')
        app = RiskApp.objects.get(name=risk_app)

        if region is None:
            raise CommandError("Input Destination Region '--region' is mandatory")

        if risk_analysis is None:
            raise CommandError("Input Risk Analysis associated to the File '--risk_analysis' is mandatory")

        if not excel_file or len(excel_file) == 0:
            raise CommandError("Input Risk Data Table '--excel_file' is mandatory")

        risk = RiskAnalysis.objects.get(name=risk_analysis, app=app)

        wb = xlrd.open_workbook(filename=excel_file)
        region = Region.objects.get(name=region)
        region_code = region.administrative_divisions.filter(parent=None)[0].code                

        axis_x = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk, axis='x')
        axis_y = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk, axis='y')
        
        sheet = wb.sheet_by_index(0)
        row_headers = sheet.row(0)            
        db = DbUtils()
        conn = db.get_db_conn()        
        first_call = True
        event_id = ''
        parent_adm_div = None
        adm_sub_units = None
        people_affected = 0
        try:
            for row_num in range(1, sheet.nrows):
                event_id = str(sheet.cell(row_num, 0).value).strip()
                iso2 = str(sheet.cell(row_num, 1).value).strip()
                dim1 = str(sheet.cell(row_num, 2).value).strip()
                dim2 = str(sheet.cell(row_num, 3).value).strip()
                attribute_value = str(sheet.cell(row_num, 4).value).strip()
                                                
                adm_div = AdministrativeDivision.objects.get(code=iso2)                
                try:
                    event = Event.objects.get(event_id=event_id)
                    event_adm_sub_units = event.nuts3.split(';')
                    adm_sub_units = AdministrativeDivision.objects.filter(code__in=event_adm_sub_units)                    
                    #update event people affected
                    '''if dim1 == 'people_affected' or dim2 == 'people_affected':
                        up_people_affected = 0 if row_num == 1 else event.people_affected                        
                        setattr(event, 'people_affected', up_people_affected + attribute_value)
                        event.save()'''
                except Event.DoesNotExist:                        
                    raise ValueError('Incorrect Event ID: {}'.format(event_id))      

                
                
                if (attribute_value != '' or allow_null_values) and any(x.value == dim1 for x in axis_x) and any(y.value == dim2 for y in axis_y):                    
                    x = axis_x.get(value=dim1)
                    y = axis_y.get(value=dim2)                                        

                    #for adm_div in adm_sub_units:
                    db_values = {
                        #'table': table_name,  # From rp.layer
                        'the_geom': geos.fromstr(adm_div.geom, srid=adm_div.srid),
                        'dim1': x.value,
                        'dim1_order': x.order,
                        'dim2': y.value,
                        'dim2_order': y.order,
                        'dim3': None,
                        'dim4': None,
                        'dim5': None,
                        'risk_analysis_id': risk.id,
                        'risk_analysis': risk_analysis,
                        'hazard_type': risk.hazard_type.mnemonic,
                        'adm_name': adm_div.name.encode('utf-8').replace("'", "''"),
                        'adm_code': adm_div.code,
                        'region': region.name,
                        'adm_level': adm_div.level,
                        'parent_adm_code': adm_div.parent.code,
                        'event_id': event.event_id,
                        'value': attribute_value                            
                    }
                    db.insert_db(conn, db_values, first_call)
                    risk_adm = RiskAnalysisAdministrativeDivisionAssociation.\
                        objects.\
                        filter(riskanalysis=risk, administrativedivision=adm_div)
                    if len(risk_adm) == 0:
                        RiskAnalysisAdministrativeDivisionAssociation.\
                            objects.\
                            create(riskanalysis=risk, administrativedivision=adm_div)
                    first_call = False                    
            #calculate aggregate values for Region (eg. Europe)
            params = { 'region': region.name, 'risk_analysis_id': risk.id }
            db.insert_aggregate_values(conn, params)
            region_adm_div = AdministrativeDivision.objects.get(region=region, level=0)
            risk_adm = RiskAnalysisAdministrativeDivisionAssociation.\
                objects.\
                filter(riskanalysis=risk, administrativedivision=region_adm_div)
            if len(risk_adm) == 0:
                RiskAnalysisAdministrativeDivisionAssociation.\
                    objects.\
                    create(riskanalysis=risk, administrativedivision=region_adm_div)

            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except:
                pass

            traceback.print_exc()
        finally:
            conn.close()
    