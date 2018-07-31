# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import traceback
import psycopg2

from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis import geos

from risks.models import Region, AdministrativeDivision
from risks.models import RiskAnalysis, RiskApp
from risks.models import RiskAnalysisDymensionInfoAssociation
from risks.models import RiskAnalysisAdministrativeDivisionAssociation

import xlrd
from xlrd.sheet import ctype_text


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
        commit = options.get('commit')
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

        risk = RiskAnalysis.objects.get(name=risk_analysis, app=app)

        wb = xlrd.open_workbook(filename=excel_file)
        region = Region.objects.get(name=region)
        region_code = region.administrative_divisions.order_by('level')[0].code #region.administrative_divisions.filter(parent=None)[0].code

        scenarios = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk, axis='x')
        round_periods = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk, axis='y')

        # print('typename = %s' % (risk.layer.typename))
        
        table_name = risk.layer.typename.split(":")[1] \
            if ":" in risk.layer.typename else risk.layer.typename

        for scenario in scenarios:
            # Dump Vectorial Data from DB
            datastore = settings.OGC_SERVER['default']['DATASTORE']
            if (datastore):
                ogc_db_name = settings.DATABASES[datastore]['NAME']
                ogc_db_user = settings.DATABASES[datastore]['USER']
                ogc_db_passwd = settings.DATABASES[datastore]['PASSWORD']
                ogc_db_host = settings.DATABASES[datastore]['HOST']
                ogc_db_port = settings.DATABASES[datastore]['PORT']

            sheet = wb.sheet_by_name(scenario.value)
            row_headers = sheet.row(0)
            for rp_idx, rp in enumerate(round_periods):
                col_num = -1
                if app.name == RiskApp.APP_DATA_EXTRACTION:
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
                elif app.name == RiskApp.APP_COST_BENEFIT:
                     col_num = 0
                                
                if col_num >= 0:                    
                    conn = self.get_db_conn(ogc_db_name, ogc_db_user, ogc_db_port, ogc_db_host, ogc_db_passwd)
                    try:
                        if app.name == RiskApp.APP_DATA_EXTRACTION:
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
                                    print('adm code read from cell: {}'.format(adm_code))
                                    
                                    #check if exists ADM unit with given code and if ADM unit belongs to given region
                                    try:
                                        adm_div = AdministrativeDivision.objects.get(code=adm_code)
                                        region_match = adm_div.regions.get(name=region.name)
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
                                    print('[%s] (%s) (%s) / %s' % (scenario.value, rp.value, adm_code, value))

                                    db_values = {
                                        'table': table_name,  # From rp.layer
                                        'the_geom': geos.fromstr(adm_div.geom, srid=adm_div.srid),
                                        'dim1': scenario.value,
                                        'dim1_order': scenario.order,
                                        'dim2': rp.value,
                                        'dim2_order': rp.order,
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
                                        'parent_adm_code': '' if parent_adm_div is None else parent_adm_div.code,
                                        'value': value
                                    }
                                    self.insert_db(conn, db_values, rp_idx)
                                    '''risk_adm = RiskAnalysisAdministrativeDivisionAssociation.\
                                        objects.\
                                        filter(riskanalysis=risk, administrativedivision=adm_div)
                                    if len(risk_adm) == 0:
                                        RiskAnalysisAdministrativeDivisionAssociation.\
                                            objects.\
                                            create(riskanalysis=risk, administrativedivision=adm_div)'''
                                    risk_adm, created = RiskAnalysisAdministrativeDivisionAssociation.objects.get_or_create(riskanalysis=risk, administrativedivision=adm_div)
                                    
                        elif app.name == RiskApp.APP_COST_BENEFIT:
                            cell_obj = sheet.cell(rp_idx + 1, 0)
                            cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
                            if cell_obj.value:
                                adm_div = AdministrativeDivision.objects.get(name=region)
                                value = sheet.cell_value(rp_idx + 1, 1)
                                print('[%s] (%s) %s / %s' % (scenario.value, rp.value, adm_div.name, value))

                                db_values = {
                                'table': table_name,  # From rp.layer
                                'the_geom': geos.fromstr(adm_div.geom, srid=adm_div.srid),
                                'dim1': scenario.value,
                                'dim1_order': scenario.order,
                                'dim2': rp.value,
                                'dim2_order': rp.order,
                                'dim3': None,
                                'dim4': None,
                                'dim5': None,
                                'risk_analysis': risk_analysis,
                                'hazard_type': risk.hazard_type.mnemonic,
                                'adm_name': adm_div.name.encode('utf-8').replace("'", "''"),
                                'adm_code': adm_div.code,
                                'region': region.name,
                                'value': value
                                }
                                self.insert_db(conn, db_values, rp_idx)
                                risk_adm = RiskAnalysisAdministrativeDivisionAssociation.\
                                objects.\
                                filter(riskanalysis=risk, administrativedivision=adm_div)
                                if len(risk_adm) == 0:
                                    RiskAnalysisAdministrativeDivisionAssociation.\
                                    objects.\
                                    create(riskanalysis=risk, administrativedivision=adm_div)

                        # Finished Import: Commit on DB
                        conn.commit()
                    except Exception:
                        try:
                            conn.rollback()
                        except:
                            pass
                        raise CommandError(e)
                        #traceback.print_exc()
                    finally:
                        conn.close()

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
        if commit:
            risk.save()

        return risk_analysis

    def get_db_conn(self, db_name, db_user, db_port, db_host, db_passwd):
        """Get db conn (GeoNode)"""
        db_host = db_host if db_host is not None else 'localhost'
        db_port = db_port if db_port is not None else 5432
        conn = psycopg2.connect(
            "dbname='%s' user='%s' port='%s' host='%s' password='%s'" % (db_name, db_user, db_port, db_host, db_passwd)
        )
        return conn

    def insert_db(self, conn, values, column_index):
        """Remove spurious records from GeoNode DB"""
        curs = conn.cursor()

        #check adm divisions
        select_template = """SELECT fid FROM adm_divisions WHERE                                        
                adm_code = '{adm_code}' AND
                level = {adm_level}"""

        curs.execute(select_template.format(**values))
        id_of_new_row = curs.fetchone()
        if id_of_new_row:
            next_table_fid = id_of_new_row[0]
        else:
            next_table_fid = None

        #check risk analysis
        select_ra_template = """SELECT id FROM risk_analysis WHERE name = '{risk_analysis}' AND hazard_type = '{hazard_type}'"""
        curs.execute(select_ra_template.format(**values))
        id_new_ra = curs.fetchone()
        if id_new_ra:
            next_ra_id = id_new_ra[0]
        else:
            next_ra_id = None

        if int(column_index) == 0:
            if next_table_fid is None:
                insert_template = """INSERT INTO adm_divisions (
                                the_geom,                          
                                adm_name, adm_code,
                                parent_adm_code, level)
                        SELECT '{the_geom}',                          
                                '{adm_name}', '{adm_code}',
                                '{parent_adm_code}', {adm_level}
                        WHERE
                        NOT EXISTS (SELECT fid FROM adm_divisions WHERE                                        
                            adm_code = '{adm_code}' AND
                            level = {adm_level})
                        RETURNING fid;"""

                curs.execute(insert_template.format(**values))
                id_of_new_row = curs.fetchone()
            
                if id_of_new_row:
                    next_table_fid = id_of_new_row[0]
                else:
                    next_table_fid = None

            if next_table_fid is None:                                            
                raise CommandError("Couldn' insert adm division!")

            if next_ra_id is None:
                insert_risk_analysis_template = """INSERT INTO risk_analysis (id, name, hazard_type)
                    SELECT {risk_analysis_id}, '{risk_analysis}', '{hazard_type}'
                    WHERE
                    NOT EXISTS (SELECT id FROM risk_analysis WHERE
                        name = '{risk_analysis}' AND
                        hazard_type = '{hazard_type}')
                    RETURNING id;"""
                
                curs.execute(insert_risk_analysis_template.format(**values))
                id_new_ra = curs.fetchone()
            
                if(id_new_ra):
                    next_ra_id = id_new_ra[0]
                
                if next_ra_id is None:                
                    raise CommandError("Could not find any suitable Risk Analysis on target DB!")
            
            rel_ids = {
                'risk_analysis_id': values['risk_analysis_id'],
                'adm_fid': next_table_fid
            }
            insert_adm_risk_analysis_relation_template = """INSERT INTO risk_analysis_adm_divisions (risk_analysis_id, adm_fid)
                SELECT {risk_analysis_id}, {adm_fid}
                WHERE NOT EXISTS (SELECT adm_fid FROM risk_analysis_adm_divisions WHERE risk_analysis_id = {risk_analysis_id} AND adm_fid = {adm_fid})
                RETURNING adm_fid"""
            #print(insert_adm_risk_analysis_relation_template.format(**rel_ids))
            curs.execute(insert_adm_risk_analysis_relation_template.format(**rel_ids))
        
        dim_ids = {
            'fid': next_table_fid,
            'ra_id': next_ra_id,
            'table': values['table'],
            'value': values['value']
        }
        for dim_idx in range(1, 6):
            dim_col = 'dim{}'.format(dim_idx)
            dim_order = 'dim{}_order'.format(dim_idx)
            if values[dim_col]:
                values['dim_col'] = dim_col
                values['dim_order'] = values[dim_order]
                values['dim_value'] = values[dim_col]
                insert_dimension_template = "INSERT INTO public.dimensions(dim_col, dim_value, dim_order) " +\
                                            "SELECT %(dim_col)s, %(dim_value)s, %(dim_order)s " +\
                                            "WHERE NOT EXISTS " +\
                                            "(SELECT dim_id FROM public.dimensions " +\
                                            "WHERE dim_col = %(dim_col)s AND dim_value = %(dim_value)s) " +\
                                            "RETURNING dim_id;"

                curs.execute(insert_dimension_template.format(**values), values)
                id_of_new_row = curs.fetchone()
                next_dim_id = None
                if id_of_new_row:
                    next_dim_id = id_of_new_row[0]

                if next_dim_id is None:
                    select_dimension_template = "SELECT dim_id FROM public.dimensions " +\
                        "WHERE dim_col = %(dim_col)s AND dim_value = %(dim_value)s;"


                    curs.execute(select_dimension_template.format(**values), values)
                    id_of_new_row = curs.fetchone()
                    if id_of_new_row:
                        next_dim_id = id_of_new_row[0]
                    else:
                        raise CommandError("Could not find any suitable Dimension on target DB!")

                dim_ids[dim_col] = next_dim_id
            else:
                dim_ids[dim_col] = 'NULL'

        insert_dimension_value_template = "INSERT INTO risk_dimensions(adm_fid, risk_analysis_id, dim1_id, dim2_id, dim3_id, dim4_id, dim5_id, value, event_id) " +\
                                          "SELECT {fid}, {ra_id}, {dim1}, {dim2}, {dim3}, {dim4}, {dim5}, '{value}', '' " +\
                                          "ON CONFLICT (adm_fid, dim1_id, dim2_id, risk_analysis_id, event_id) DO UPDATE " +\
                                          "SET value = '{value}';"
                                                                                    
        curs.execute(insert_dimension_value_template.format(**dim_ids))
    
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def to_int_if_number(self, s):
        try:
            return int(float(s))
        except ValueError:
            return s        

