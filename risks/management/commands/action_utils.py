import traceback
import psycopg2

from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis import geos

class DbUtils:

    def get_db_conn(self):
        datastore = settings.OGC_SERVER['default']['DATASTORE']
        if (datastore):
            db_name = settings.DATABASES[datastore]['NAME']
            db_user = settings.DATABASES[datastore]['USER']
            db_passwd = settings.DATABASES[datastore]['PASSWORD']
            db_host = settings.DATABASES[datastore]['HOST']
            db_port = settings.DATABASES[datastore]['PORT']

        db_host = db_host if db_host is not None else 'localhost'
        db_port = db_port if db_port is not None else 5432
        conn = psycopg2.connect(
            "dbname='%s' user='%s' port='%s' host='%s' password='%s'" % (db_name, db_user, db_port, db_host, db_passwd)
        )
        return conn
        
            
    def insert_aggregate_values(self, conn, params):
        curs = conn.cursor()   

        insert_template = """INSERT INTO risk_dimensions (adm_fid, dim1_id, dim2_id, risk_analysis_id, value, event_id)
            select 
                rfid.fid as adm_fid, 
                dim1_id, 
                dim2_id, 
                {risk_analysis_id} as risk_analysis_id, 
                sum(case when value = '' then 0 else value::float end) as value, 
                '' as event_id
            from risk_dimensions rd
            join dimensions d on d.dim_id = rd.dim1_id
            join dimensions d2 on d2.dim_id = rd.dim2_id
            join adm_divisions adm on adm.fid = rd.adm_fid
            join risk_analysis ra on ra.id = rd.risk_analysis_id
            join (
                select fid, adm_code from adm_divisions where adm_code = '{adm_code}' and "level" = {level}
            ) rfid on rfid.adm_code = adm.parent_adm_code 
            where risk_analysis_id = {risk_analysis_id}
            and adm.fid <> rfid.fid
            group by rfid.fid, risk_analysis_id, dim1_id, dim2_id
            ON CONFLICT (adm_fid, dim1_id, dim2_id, risk_analysis_id, event_id) DO UPDATE
            SET value = excluded.value"""
        
        for adm_div in params['adm_to_process']:
            values = {
                'risk_analysis_id': params['risk_analysis_id'],
                'adm_code': adm_div.code,
                'level': adm_div.level
            }
        
            curs.execute(insert_template.format(**values))
    
    
    def insert_event(self, conn, values):
        curs = conn.cursor()

        insert_template = """INSERT INTO events (
                                event_id,
                                begin_date,
                                end_date)
                            SELECT '{event_id}',
                                    '{begin_date}',
                                    '{end_date}'
                            ON CONFLICT (event_id) DO UPDATE
                            SET begin_date = '{begin_date}', end_date = '{end_date}'"""
        
        curs.execute(insert_template.format(**values))
    
    
    def insert_db(self, conn, values, first_call):        
        curs = conn.cursor()

        '''insert_template = """INSERT INTO events (
                                event_id,
                                begin_date,
                                end_date)
                            SELECT '{event_id}',
                                    '{begin_date}',
                                    '{end_date}'
                            ON CONFLICT (event_id) DO UPDATE
                            SET begin_date = '{begin_date}', end_date = '{end_date}'"""
        
        curs.execute(insert_template.format(**values))'''

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
        next_table_fid = None
        if id_of_new_row:
            next_table_fid = id_of_new_row[0]
        else:
            next_table_fid = None

        if next_table_fid is None:
            select_template = """SELECT fid FROM adm_divisions WHERE                                        
                    adm_code = '{adm_code}' AND
                    level = {adm_level} """

            curs.execute(select_template.format(**values))
            id_of_new_row = curs.fetchone()
            if id_of_new_row:
                next_table_fid = id_of_new_row[0]
            else:
                raise CommandError("Could not find adm division on target DB!")

        #print('column index = {}'.format(new_adm))
            
        select_ra_template = """SELECT id FROM risk_analysis WHERE name = '{risk_analysis}' AND hazard_type = '{hazard_type}'"""
        curs.execute(select_ra_template.format(**values))
        id_new_ra = curs.fetchone()
        if id_new_ra:
            next_ra_id = id_new_ra[0]
        else:
            next_ra_id = None
                
        if first_call and next_ra_id is None:
            insert_risk_analysis_template = """INSERT INTO risk_analysis (name, hazard_type, region)
                SELECT '{risk_analysis}', '{hazard_type}', '{region}'
                WHERE
                NOT EXISTS (SELECT id FROM risk_analysis WHERE
                    name = '{risk_analysis}' AND
                    hazard_type = '{hazard_type}' AND
                    region = '{region}')
                RETURNING id;"""
            
            curs.execute(insert_risk_analysis_template.format(**values))
            id_new_ra = curs.fetchone()
            
            if(id_new_ra):
                next_ra_id = id_new_ra[0]
            
            if next_ra_id is None:                
                raise CommandError("Could not find any suitable Risk Analysis on target DB!")
            
        rel_ids = {
            'risk_analysis_id': next_ra_id,
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
            #'table': values['table'],
            'event_id': values['event_id'],
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

        insert_dimension_value_template = "INSERT INTO risk_dimensions(adm_fid, risk_analysis_id, dim1_id, dim2_id, dim3_id, dim4_id, dim5_id, event_id, value) " +\
                                          "SELECT {fid}, {ra_id}, {dim1}, {dim2}, {dim3}, {dim4}, {dim5}, '{event_id}', '{value}' " +\
                                          "ON CONFLICT (adm_fid, dim1_id, dim2_id, risk_analysis_id, event_id) DO UPDATE " +\
                                          "SET value = '{value}';"       
        curs.execute(insert_dimension_value_template.format(**dim_ids))        
