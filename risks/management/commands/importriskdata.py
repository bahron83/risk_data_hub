import traceback

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from risks.models import Region, AdministrativeDivision
from risks.models import DamageAssessment, RiskApp
from risks.models import DamageTypeValue

import xlrd
from xlrd.sheet import ctype_text


class Command(BaseCommand):    

    help = 'Import Risk Data: Loss Impact and Impact Analysis Types.'

    def add_arguments(self, parser):        
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
            '-m',
            '--excel-metadata-file',
            dest='excel_metadata_file',
            type=str,
            help='Input Risk Metadata Table as XLSX File.')
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
        return parser

    def handle(self, **options):        
        region = options.get('region')
        excel_file = options.get('excel_file')
        risk_analysis = options.get('risk_analysis')
        excel_metadata_file = options.get('excel_metadata_file')
        risk_app =  options.get('risk_app')
        app = RiskApp.objects.get(name=risk_app)

        if region is None:
            raise CommandError("Input Destination Region '--region' is mandatory")

        if risk_analysis is None:
            raise CommandError("Input Risk Analysis associated to the File '--risk_analysis' is mandatory")

        if not excel_file or len(excel_file) == 0:
            raise CommandError("Input Risk Data Table '--excel_file' is mandatory")

        risk = DamageAssessment.objects.get(name=risk_analysis, app=app)
        region = Region.objects.get(name=region)        
        wb = xlrd.open_workbook(filename=excel_file)        
        scenarios = DamageTypeValue.objects.filter(damage_assessment=risk, axis='x')
        return_periods = DamageTypeValue.objects.filter(damage_assessment=risk, axis='y')                                
        for scenario in scenarios:            
            sheet = wb.sheet_by_name(scenario.value)
            print 'reading from sheet {}'.format(scenario.value)
            row_headers = sheet.row(0)
            for rp_idx, rp in enumerate(round_periods):
                col_num = -1
                
                for idx, cell_obj in enumerate(row_headers):
                    # cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
                    # print('(%s) %s %s' % (idx, cell_type_str, cell_obj.value))
                    try:
                        # if int(cell_obj.value) == int(rp.value):
                        # print('{} =? {}'.format(rp.value, cell_obj.value))
                        if self.to_int_if_number(str(cell_obj.value).strip()) == self.to_int_if_number(str(rp.value).strip()):
                            # print('[%s] (%s) RP-%s' % (scenario.value, idx, rp.value))
                            col_num = idx
                            break
                    except:
                        traceback.print_exc()
                        pass                
                                
                if col_num >= 0:                                                            
                    for row_num in range(1, sheet.nrows):
                        cell_obj = sheet.cell(row_num, 5)
                        iso_country = str(sheet.cell(row_num, 2).value)[:2]
                        cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
                        value = sheet.cell(row_num, col_num).value if self.is_number(sheet.cell(row_num, col_num).value) else None
                        # print('(%s) %s %s' % (idx, cell_type_str, cell_obj.value))
                        if cell_obj.value and value is not None:
                            adm_code = cell_obj.value \
                                if cell_type_str == 'text' \
                                else iso_country + '{:05d}'.format(int(cell_obj.value))
                            #print('adm code read from cell: {}'.format(adm_code))
                                                            
                            try:
                                adm_div = AdministrativeDivision.objects.get(code=adm_code)                                    
                            except AdministrativeDivision.DoesNotExist:
                                traceback.print_exc()
                                pass                                    
                            
                            parent_adm_div = None
                            if adm_div.parent is not None:
                                try:                                            
                                    parent_adm_div = AdministrativeDivision.objects.get(id=adm_div.parent.id)                                        
                                except AdministrativeDivision.DoesNotExist:
                                    traceback.print_exc()
                                    pass
                            #print('parent_adm_div = {}'.format(parent_adm_div.name))
                            
                            #print('[%s] (%s) %s (%s) / %s' % (scenario.value, rp.value, adm_div.name.encode('utf-8'), adm_code, value))
                            #print('[%s] (%s) (%s) / %s' % (scenario.value, rp.value, adm_code, value))                        
                            
                            current_row_key = '{}_{}_{}'.format(scenario.id, rp.id, adm_div.id)                            
                            
                            risk.values[current_row_key] = {
                                'dim1': scenario.id,
                                'dim2': rp.id,                                                                                                                                
                                'administrative_division_id': adm_div.id,
                                'value': value                                
                            }
                            if not risk.administrative_divisions.filter(pk=adm_div.pk).exists():
                                risk.administrative_divisions.add(adm_div)                                                                                                                    
        
        # Import or Update Metadata if Metadata File has been specified/found
        if excel_metadata_file:
            call_command('importriskmetadata',
                         region=region.name,
                         excel_file=excel_metadata_file,
                         risk_analysis=risk_analysis,
                         risk_app=[app.name])
            risk.metadata_file = excel_metadata_file

        # Finalize
        risk.data_file = excel_file
        risk.region = region        
        risk.save()

        return risk_analysis