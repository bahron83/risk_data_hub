import traceback
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from risks.models import RiskAnalysis, RiskAnalysisDymensionInfoAssociation
from action_utils import DbUtils


class Command(BaseCommand):
    help = 'Fix Risk Analysis Dimension Info associations'

    axis_mapping = {'x': 'dim1', 'y': 'dim2'}

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
            '--risk-analysis-id',            
            dest='risk_analysis_id',
            default='',
            type=str,
            help='Risk Analysis to be fixed')              
        return parser

    def handle(self, **options):
        commit = options.get('commit')        
        risk_analysis_id = options.get('risk_analysis_id')        
        db = DbUtils()
        ogc_conn = db.get_db_conn()
        ogc_dim_infos = ogc_conn.cursor() 
        curs = ogc_conn.cursor()

        select_template = """SELECT * FROM (
                                SELECT dim_id, dim_col, dim_value, dim_order, risk_analysis_id
                                FROM risk_dimensions rd
                                JOIN dimensions d1 on d1.dim_id = rd.dim1_id
                                WHERE risk_analysis_id = {risk_analysis_id}
                                GROUP BY dim_id, dim_col, dim_value, dim_order, risk_analysis_id

                                UNION 

                                SELECT dim_id, dim_col, dim_value, dim_order, risk_analysis_id
                                FROM risk_dimensions rd
                                JOIN dimensions d2 on d2.dim_id = rd.dim2_id
                                WHERE risk_analysis_id = {risk_analysis_id}
                                GROUP BY dim_id, dim_col, dim_value, dim_order, risk_analysis_id
                                ) sel
                            ORDER BY  dim_col, dim_order;""" 

        update_template = """UPDATE risk_dimensions
                                SET {dim_col} = {dim_new_id}
                                WHERE risk_analysis_id = {risk_analysis_id}
                                AND {dim_col} = {dim_old_id};"""      

        insert_template = """INSERT INTO dimensions (dim_col, dim_value, dim_order) 
                                SELECT '{dim_col}', '{dim_value}', {dim_order}                                
                                RETURNING dim_id;"""

        select_dim_template = """SELECT dim_id 
                                    FROM dimensions 
                                    WHERE dim_col = '{dim_col}' 
                                    AND dim_value = '{dim_value}'
                                    AND dim_order = {dim_order};"""

        try:
            if risk_analysis_id:
                try:
                    risk_analysis_list = [RiskAnalysis.objects.get(id=risk_analysis_id)]
                except RiskAnalysis.DoesNotExist:
                    raise CommandError("Could not find Risk Analysis with id {}".format(risk_analysis_id))
            else: 
                risk_analysis_list = RiskAnalysis.objects.all()
            for risk_analysis in risk_analysis_list:
                params = {
                    'risk_analysis_id': risk_analysis.id
                }                
                dim_infos = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk_analysis).order_by('axis', 'order').values()

                ogc_dim_infos.execute(select_template.format(**params))
                
                for dim_info in dim_infos:                
                    for ogc_dim_info in ogc_dim_infos:                                        
                        if ogc_dim_info[1] == self.axis_mapping[dim_info['axis']] and ogc_dim_info[3] == dim_info['order']:
                            if ogc_dim_info[2] != dim_info['value']:
                                
                                ins_values = {
                                    'dim_col': ogc_dim_info[1],
                                    'dim_value': dim_info['value'],
                                    'dim_order': dim_info['order']
                                }
                                curs.execute(select_dim_template.format(**ins_values))
                                #print(select_dim_template.format(**ins_values))
                                ogc_dim_new = curs.fetchone()
                                if ogc_dim_new:
                                    ogc_dim_id = ogc_dim_new[0]
                                else:
                                    curs.execute(insert_template.format(**ins_values))
                                    ogc_dim_new = curs.fetchone()
                                    ogc_dim_id = ogc_dim_new[0]
                                    
                                up_values = {
                                    'dim_col': ogc_dim_info[1] + '_id',
                                    'dim_new_id': ogc_dim_id,
                                    'dim_old_id': ogc_dim_info[0],
                                    'risk_analysis_id': risk_analysis.id
                                }
                                curs.execute(update_template.format(**up_values))
                                #print(update_template.format(**up_values))

            if commit:
                ogc_conn.commit()
        except Exception:
            try:
                ogc_conn.rollback()
            except:
                pass

            traceback.print_exc()
        finally:
            ogc_conn.close()   
    