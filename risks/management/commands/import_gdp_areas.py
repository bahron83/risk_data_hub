import os
import traceback
from optparse import make_option
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from risks.models import AdministrativeDivision, AdministrativeData, AdministrativeDivisionDataAssociation

import xlrd

DATASETS = ['GDP','Population','Area']
ADMCODE = 5
FIRST_VALUE_COLUMN = 6

def parse_float(string):
    try:
        return float(string)
    except ValueError:
        return False

def to_int_if_number(string):
    f = parse_float(string)
    if f:
        return int(f)
    else:
        return string

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--commit',
            action='store_true',
            dest='commit',
            default=True,
            help='Commits Changes to the storage.')
        return parser    

    def handle(self, **options):
        commit = options.get('commit')        
        basedir = "/home/geonode/import_data/countries"
        allowed_extensions = [".xlsx"]
                
        for file in os.listdir(basedir):
            if file.endswith(tuple(allowed_extensions)):                    
                wb = xlrd.open_workbook(filename=os.path.join(basedir, file))

                for dataset in DATASETS:
                    print('start importing {}'.format(dataset))
                    sheet = wb.sheet_by_name(dataset)
                    row_headers = sheet.row(0)
                    col_num = 0
                    for idx, cell_obj in enumerate(row_headers):
                        col_num += 1
                        if idx >= FIRST_VALUE_COLUMN:  
                            print('coloumn n. {}'.format(idx))
                            for row_num in range(1, sheet.nrows):
                                adm_code = sheet.cell(row_num, ADMCODE).value
                                try:
                                    adm_div = AdministrativeDivision.objects.get(code=adm_code)                                        
                                except AdministrativeDivision.DoesNotExist:
                                    traceback.print_exc()
                                    pass
                                
                                dimension = to_int_if_number(sheet.cell(0, idx).value)
                                value = sheet.cell(row_num, idx).value
                                if value:
                                    admin_data, created = AdministrativeData.objects.get_or_create(name=dataset)
                                    association, created = AdministrativeDivisionDataAssociation.objects.get_or_create(
                                        adm=adm_div,
                                        data=admin_data,
                                        dimension=dimension
                                    )
                                    association_updated = AdministrativeDivisionDataAssociation.objects.filter(pk=association.pk).update(value=value)                                

                                
                                    print('Imported data: ADM = {} - TYPE = {} - DIMENSION = {} - VALUE = {}'.format(adm_div.code, dataset, dimension, value))
                                    