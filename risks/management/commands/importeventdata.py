import traceback
import xlrd
import datetime
from dateutil.parser import parse
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from risks.models import (Region, AdministrativeDivision, Event, Phenomenon, DamageAssessment, DamageAssessmentEntry,
                            RiskApp, DamageTypeValue, AssetItem, Hazard, AttributeSet)


COMMIT_SIZE = 10000
HEADER_ROWS = 1

def is_last_row(row_num, nrows):
    return row_num >= nrows - HEADER_ROWS

class Command(BaseCommand):
    help = 'Import Event Data: phenomena and impacts'

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
            '-k',
            '--risk-damage-assessment',
            dest='damage_assessment',
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
        region_name = options.get('region')
        excel_file = options.get('excel_file')
        damage_assessment = options.get('damage_assessment')        
        risk_app =  options.get('risk_app')        
        app = RiskApp.objects.get(name=risk_app)

        if region_name is None:
            raise CommandError("Input Destination Region '--region' is mandatory")

        if damage_assessment is None:
            raise CommandError("Input Risk Analysis associated to the File '--damage_assessment' is mandatory")

        if not excel_file or len(excel_file) == 0:
            raise CommandError("Input Risk Data Table '--excel_file' is mandatory")

        risk = DamageAssessment.objects.get(name=damage_assessment, app=app)

        wb = xlrd.open_workbook(filename=excel_file)
        region = Region.objects.get(name=region_name)        

        axis_x = DamageTypeValue.objects.filter(damage_assessment=risk, axis='x')
        axis_y = DamageTypeValue.objects.filter(damage_assessment=risk, axis='y')
        
        sheet = wb.sheet_by_index(0)
        row_headers = sheet.row(0)                    
        code = ''
        sample_adm_div = None
        prev_obj = None
        prev_event = None        
        entry = {}
        insert_rows = []
        event_codes = []                
        
        for row_num in range(HEADER_ROWS, sheet.nrows):  
            obj = {}                                    
            duplicates = []             
            obj['code'] = str(sheet.cell(row_num, 0).value).strip() # empty for new data
            hazard_type_str = str(sheet.cell(row_num, 1).value).strip()
            adm_code = str(sheet.cell(row_num, 2).value).strip() # can be any administrative division
            obj['year'] = int(sheet.cell(row_num, 3).value)                                
            obj['begin_date'] = parse_date(sheet.cell(row_num, 4).value)
            obj['end_date'] = parse_date(sheet.cell(row_num, 5).value)
            value_event = str(sheet.cell(row_num, 6).value).strip()
            dim1_value = str(sheet.cell(row_num, 7).value).strip()
            dim2_value = str(sheet.cell(row_num, 8).value).strip()
            phenomenon_begin_date = parse_date(sheet.cell(row_num, 9).value)
            phenomenon_end_date = parse_date(sheet.cell(row_num, 10).value)            
            value_phenomenon = str(sheet.cell(row_num, 11).value).strip()
            geometry = str(sheet.cell(row_num, 12).value).strip()
            item_id = str(sheet.cell(row_num, 13).value).strip()
            linked_item_id = str(sheet.cell(row_num, 14).value).strip()
                                                                                        
            if obj['begin_date'] is None or obj['end_date'] is None:
                raise CommandError('Missing or incorrect date for Event at line {}'.format(row_num))
            
            if phenomenon_begin_date is None:
                phenomenon_begin_date = obj['begin_date']

            if phenomenon_end_date is None:
                phenomenon_end_date = obj['end_date']
            
            try:
                obj['attribute_set'] = AttributeSet.objects.get(name='default')
            except AttributeSet.DoesNotExist:
                raise CommandError('Cannot find default Attribute Set')
            
            try:
                obj['hazard_type'] = Hazard.objects.get(mnemonic=hazard_type_str)
            except Hazard.DoesNotExist:
                raise CommandError('Invalid Hazard Type: {}'.format(hazard_type_str))
            
            administrative_division = None
            try:
                administrative_division = AdministrativeDivision.objects.get(code=adm_code)
                if administrative_division.level == 1:
                    obj['country'] = administrative_division
                elif administrative_division.level > 1:
                    country = [adm for adm in administrative_division.get_parents_chain() if adm.level == 1]
                    if country:
                        obj['country'] = country[0]
            except AdministrativeDivision.DoesNotExist:                        
                raise CommandError('Incorrect Administrative Division: {}'.format(adm_code))                 
            
            # Save Event
            event = None
            obj['region'] = region
            if obj['code']:                   
                if row_num == HEADER_ROWS or obj['code'] != prev_obj['code']:
                    try:
                        event = Event.objects.get(code=obj['code'], region=region)
                        for key, value in obj.items():
                            setattr(event, key, value)                    
                        event.save()
                    except Event.DoesNotExist:                                                        
                        obj['state'] = 'draft'
                        event = Event(**obj)
                        event.save()                         
            else:
                if prev_obj:
                    prev_code = prev_obj['code']
                    prev_obj['code'] = ''
                    prev_obj.pop('state', None)                                
                if obj != prev_obj:                                      
                    new_code, duplicates = Event.generate_event_code(obj['hazard_type'], obj['country'], obj['begin_date'], region) 
                    obj['code'] = new_code                    
                    obj['state'] = 'ready'
                    if len(duplicates) < 2:                                                
                        if len(duplicates) > 0:
                            obj['state'] = 'draft' 
                        event = Event(**obj)
                        event.save()
                    else:
                        try:
                            event = Event.find_exact_match(obj)
                            obj['code'] = event.code
                        except:
                            raise CommandError('Unexpected error during lookup for event')
                else:
                    obj['code'] = prev_code
                    try:
                        event = Event.objects.get(code=prev_code, region=region)
                    except:
                        raise CommandError('Unexpected error during lookup for event code {}'.format(prev_code))
            event.refresh_from_db() 
            event_export = event.export()
            prev_obj = obj

            #append event id to return list                        
            formatted_text_row = '{}\tSuspected duplicate of {}'.format(event.code, ';'.join(duplicates)) if duplicates else event.code
            event_codes.append(formatted_text_row)

            # Save Phenomenon
            phenomenon, created = Phenomenon.objects.get_or_create(
                event=event,
                administrative_division=administrative_division,
                begin_date=phenomenon_begin_date,
                end_date=phenomenon_end_date
            )
            phenomenon_export = phenomenon.export()
            phenomenon_export['value'] = value_phenomenon

            # Save DamageAssessmentEntry                        
            '''if dim1_value and dim2_value:
                dim1 = axis_x.filter(value=dim1_value).first()
                dim2 = axis_y.filter(value=dim2_value).first()                
                if event != prev_event:
                    if prev_event:
                        self.prepare_entry(entry, insert_rows)
                    
                    #create new entry
                    entry = {
                        'region': region.name,
                        'country': event.country.code,
                        'damage_assessment': risk.name,
                        'event_code': event.code,
                        'dim1': dim1.export(dim1.EXPORT_FIELDS_ANALYSIS),
                        'dim2': dim2.export(dim2.EXPORT_FIELDS_ANALYSIS), 
                        'phenomena': [],
                        'year': event.year,                                                                                                                                                    
                        'value': value_event                                
                    }

                #continue constructing current entry                
                if geometry:
                    phenomenon_export['geometry'] = geometry #validate geojson
                if item_id:
                    try:
                        AssetItem.objects.get(id=item_id)
                        phenomenon_export['item_id'] = item_id
                    except:
                        raise CommandError('Invalid ID for Asset Item: {}'.format(item_id))
                if linked_item_id:
                    try:
                        AssetItem.objects.get(id=linked_item_id)
                        phenomenon_export['linked_item_id'] = linked_item_id
                    except:
                        raise CommandError('Invalid ID for Asset Item: {}'.format(item_id))                            
                entry['phenomena'].append(phenomenon_export)

                if event == prev_event and is_last_row(row_num, sheet.nrows):
                    self.prepare_entry(entry, insert_rows)
                
                if len(insert_rows) >= COMMIT_SIZE:
                    DamageAssessmentEntry.objects.bulk_create(insert_rows)
                    insert_rows[:] = []                                                                                                                                    
            
            prev_event = event'''

            if dim1_value and dim2_value:
                dim1 = axis_x.filter(value=dim1_value).first()
                dim2 = axis_y.filter(value=dim2_value).first()                                
                    
                #create new entry
                entry = {
                    'region': region.name,
                    'damage_assessment': risk.name,
                    'dim1': dim1.export(dim1.EXPORT_FIELDS_ANALYSIS),
                    'dim2': dim2.export(dim2.EXPORT_FIELDS_ANALYSIS), 
                    'administrative_division': administrative_division.export(administrative_division.EXPORT_FIELDS_ANALYSIS),
                    'value': value_event,
                    'event': event_export               
                }

                #continue constructing current entry                
                if geometry:
                    phenomenon_export['geometry'] = geometry #validate geojson
                if item_id:
                    try:
                        AssetItem.objects.get(id=item_id)
                        phenomenon_export['item_id'] = item_id
                    except:
                        raise CommandError('Invalid ID for Asset Item: {}'.format(item_id))
                if linked_item_id:
                    try:
                        AssetItem.objects.get(id=linked_item_id)
                        phenomenon_export['linked_item_id'] = linked_item_id
                    except:
                        raise CommandError('Invalid ID for Asset Item: {}'.format(item_id))                            
                entry['phenomenon'] = phenomenon_export
                
                self.prepare_entry(entry, insert_rows)
                
                if len(insert_rows) >= COMMIT_SIZE:
                    DamageAssessmentEntry.objects.bulk_create(insert_rows)
                    insert_rows[:] = []                                                                                                                                                

            # Insert DamegeAssessment/AdmDivision relation for fast location lookups
            locations = [administrative_division] + administrative_division.get_parents_chain()
            for loc in locations:
                if not risk.administrative_divisions.filter(pk=loc.pk).exists():
                    risk.administrative_divisions.add(loc)

        # Finish bulk insert
        if len(insert_rows) > 0:
            DamageAssessmentEntry.objects.bulk_create(insert_rows)

        return '\r\n'.join(event_codes)
    
    def prepare_entry(self, entry, insert_rows): 
        if 'damage_assessment' in entry and 'phenomenon' in entry:
            da_entry = DamageAssessmentEntry.objects.filter(entry__damage_assessment=entry['damage_assessment'], entry__phenomenon__id=entry['phenomenon']['id'])
            if da_entry.exists():
                da_entry.update(entry=entry)                
            else:                
                da_entry = DamageAssessmentEntry(entry=entry)
                insert_rows.append(da_entry)

def is_number(s, default=None):
    try:
        res = float(s)
    except ValueError:
        return False
    return True

def parse_date(date, auto_assign=False):
    res_date = datetime.date(datetime.datetime.now().year, 1, 1) if auto_assign else None
    if is_number(date):                    
        try:
            res_date = xlrd.xldate_as_datetime(date, 0)            
        except:
            pass
    else:
        try:
            res_date = parse(date)            
        except ValueError:
            pass   
    return res_date