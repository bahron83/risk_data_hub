import re
from django.core.management.base import BaseCommand
from risks.management.commands.action_utils import DbUtils
from risks.models import RiskAnalysis, EventRiskAnalysisAssociation, Event


class Command(BaseCommand):
    def handle(self, **options):
        db = DbUtils()
        conn = db.get_db_conn()        
        curs = conn.cursor()

        select_from_gsdb = """select ev.event_id as event_id, array_agg(distinct(ra.name)) as ra
                                from events ev
                                left join risk_dimensions rd on rd.event_id = ev.event_id
                                left join risk_analysis ra on ra.id = rd.risk_analysis_id
                                group by ev.event_id"""

        replace_pattern = r'\{(w+),(w+)\}'
        
        curs.execute(select_from_gsdb)
        rows = []
        while True:
            row = curs.fetchone()
            if row == None:
                break
            #temp = re.sub(replace_pattern, r"\1','\2", row[1])
            #temp = row[1].replace('{', '')
            #temp = temp.replace('}', '')
            #print('current row: {}'.format(row[0], temp))
            #adjusted_row = (row[0], temp.split(','))
            print('current row: {}'.format(row))
            rows.append(row)    
        conn.close()

        for r in rows:
            try:
                event = Event.objects.get(event_id=r[0])            
            except Event.DoesNotExist:
                pass
            if event:                
                for risk in RiskAnalysis.objects.filter(name__in=r[1]):
                    assoc, created = EventRiskAnalysisAssociation.objects.get_or_create(event=event, risk=risk)
                    print('created assoc {}'.format(assoc))
