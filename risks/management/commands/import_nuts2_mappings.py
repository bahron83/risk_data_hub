import os
import traceback
from optparse import make_option
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from risks.models import AdministrativeDivision, AdministrativeDivisionMappings

import xlrd


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
                
        for fname in os.listdir(basedir):
            if fname.endswith(tuple(allowed_extensions)):                    
                wb = xlrd.open_workbook(filename=os.path.join(basedir, fname))
                sheet = wb.sheet_by_index(0)
                
                print('start importing file {}'.format(fname))
                for row_num in range(1, sheet.nrows):
                    parent_code = str(sheet.cell(row_num, 0).value).strip()
                    child_code = str(sheet.cell(row_num, 1).value).strip()
                    code = str(sheet.cell(row_num, 2).value).strip()
                    name = sheet.cell(row_num, 3).value

                    try:
                        parent_adm_div = AdministrativeDivision.objects.get(code=parent_code)
                    except AdministrativeDivision.DoesNotExist:
                        raise ValueError('No adm unit found with code: {}'.format(parent_code))                  

                    try:
                        child_adm_div = AdministrativeDivision.objects.get(code=child_code)
                    except AdministrativeDivision.DoesNotExist:
                        raise ValueError('No adm unit found with code: {}'.format(child_code)) 

                    adm_mapping, created = AdministrativeDivisionMappings.objects.get_or_create(parent=parent_adm_div, child=child_adm_div)
                    updated = AdministrativeDivisionMappings.objects.filter(pk=adm_mapping.id).update(code=code, name=name)

                    print('imported {} - {}'.format(code, unicode(name).encode('utf8')))
