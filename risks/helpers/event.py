from django.contrib.gis import geos
from risks.management.commands.action_utils import DbUtils
from risks.models import AdministrativeDivision, Event, AdministrativeDivisionMappings, EventRiskAnalysisAssociation
from risks.models import (RiskAnalysisAdministrativeDivisionAssociation, EventAdministrativeDivisionAssociation, 
                            EventFurtherAdministrativeDivisionAssociation, RiskAnalysisDymensionInfoAssociation)


class EventHelper(object):
    _event = None

    def __init__(self, event=None):
        self._event = event

    def get_event(self):
        return self._event
    
    def set_event(self, event):
        self._event = event        

    def set_adm_associations(self):
        if self._event:
            try:
                country = AdministrativeDivision.objects.get(code=self._event.iso2, level=1)
            except AdministrativeDivision.DoesNotExist:
                pass 
            adm_link, created = EventAdministrativeDivisionAssociation.objects.update_or_create(event=self._event, adm=country)
            if self._event.nuts3:
                nuts3_list = self._event.nuts3.split(';')
                nuts2_matches = AdministrativeDivisionMappings.objects.filter(child__code__in=nuts3_list).distinct()
                if nuts2_matches:
                    for nuts2 in nuts2_matches:
                        EventFurtherAdministrativeDivisionAssociation.objects.update_or_create(event=self._event, f_adm=nuts2)
                for adm_code in nuts3_list:                    
                    try:
                        adm_div = AdministrativeDivision.objects.get(regions__id__exact=self._event.region.id, code=adm_code)
                        adm_link, created = EventAdministrativeDivisionAssociation.objects.update_or_create(event=self._event, adm=adm_div)                        
                    except AdministrativeDivision.DoesNotExist:                
                        pass 

    def insert_attributes_row(self, params):                 
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
            'event_id': params['event'].id,
            'begin_date': params['event'].begin_date,
            'end_date': params['event'].end_date,
            'value': params['attribute_value']
        }
        db = DbUtils()
        db.insert_db(params['conn'], db_values, params['first_call'])
        if params['create_django_association']:
            risk_adm, created = RiskAnalysisAdministrativeDivisionAssociation.objects.get_or_create(riskanalysis=params['risk'], administrativedivision=params['adm_div'])
            #event_adm, created = EventAdministrativeDivisionAssociation.objects.get_or_create(event=params['event'], adm=params['adm_div'])

    def insert_aggregate_values(conn, sample_adm_div = None, adm_level_precision = 2):
        region_adm_div = None
        if sample_adm_div:
            region_adm_div = [adm for adm in sample_adm_div.get_parents_chain() if adm.level == 0] 
        else:
            try:
                region_adm_div = [AdministrativeDivision.objects.get(name__icontains='Europe', level=0)]
            except:
                pass
        if region_adm_div:
            db = DbUtils()                    
            adm_to_process = region_adm_div
            if adm_level_precision == 2:
                adm_to_process.append(AdministrativeDivision.objects.filter(parent=region_adm_div[0], level=1))
            params = { 'adm_to_process': adm_to_process , 'risk_analysis_id': risk.id }
            db.insert_aggregate_values(conn, params)            
            risk_adm, created = RiskAnalysisAdministrativeDivisionAssociation.objects.get_or_create(riskanalysis=risk, administrativedivision=region_adm_div[0])
    
    def insert_event_attributes(self, data_attributes, conn):
        first_call = True
        if data_attributes:
            for a in data_attributes:
                event = a['event']
                if a['risk_analysis']:
                    for risk in a['risk_analysis']:                        
                        axis_x = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk, axis='x')
                        axis_y = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=risk, axis='y')
                        x = axis_x.get(value=str(a['dim1']))
                        y = axis_y[0]
                        attribute_value = a[str(a['dim1'])]

                        params = {
                            'adm_div': a['adm_div'],
                            'event': event,
                            'risk': risk,
                            'region': risk.region,
                            'attribute_value': attribute_value,
                            'x': x,
                            'y': y,
                            'first_call': first_call,
                            'create_django_association': True,                        
                            'conn': conn
                        }
                        self.insert_attributes_row(params)
                        event_risk, created = EventRiskAnalysisAssociation.objects.get_or_create(risk=risk, event=event)
                        first_call = False
            self.insert_aggregate_values()

    def sync_geodb(self, queryset):
        db = DbUtils()
        conn = db.get_db_conn()        
        rows_updated = 0
        if queryset:
            try:
                for event in queryset:                
                    code = event.code
                    if not code:
                        try:
                            country = AdministrativeDivision.objects.get(code=event.iso2, level=1)
                        except AdministrativeDivision.DoesNotExist:                        
                            pass
                        code, duplicates = Event.generate_code(event.hazard_type, country, event.begin_date, event.region)
                    if event.state != 'ready':
                        try:
                            Event.objects.filter(pk=event.pk).update(state='ready', code=str(code))
                        except:                        
                            pass
                        event.refresh_from_db()
                        event_dict = {
                            'event_id': event.id,
                            'begin_date': event.begin_date,
                            'end_date': event.end_date,
                            'state': event.state
                        }
                        db.insert_event(conn, event_dict)                        
                        rows_updated += 1
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
        
        return rows_updated
