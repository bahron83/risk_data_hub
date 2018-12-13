from django.contrib.gis import geos
from django.db import transaction
from risks.management.commands.action_utils import DbUtils
from risks.models.location import AdministrativeDivision
from risks.models.event import Event, Phenomenon
from risks.models.eav_attribute import EavAttribute
from risks.models.damage_type import DamageTypeValue
from risks.models.risk_analysis import DamageAssessmentValue


class EventHelper(object):
    _event = None
    _phenomena = None

    def __init__(self, event=None, phenomena=None):
        self._event = event
        self._phenomena = phenomena

    def get_event(self):
        return self._event
    
    def set_event(self, event):
        self._event = event        

    def get_phenomena(self):
        return self._phenomena
    
    def set_phenomena(self, phenomena):
        self._phenomena = phenomena

    def save_event(self, event_obj, phenomena_list=None):
        event_fields = Event.get_fields_basic()
        additional_attributes = []
        for t in event_obj.items():
            key = t[0][0]
            if key not in event_fields:
                additional_attributes.apppend({key: event_obj[key]})
                del event_obj[key]

        event = Event(**event_obj)        
        event.save() 
        event.refresh_from_db() 

        if additional_attributes:
            for a in additional_attributes:
                key = a.items()[0][0]
                eav = None
                try:
                    eav = EavAttribute.objects.get(code=key)
                except EavAttribute.DoesNotExist:
                    continue
                if eav.data_type == 'varchar':
                    attr = EventAttributeValueVarchar()
                elif eav.data_type == 'text':
                    attr = EventAttributeValueText()
                elif eav.data_type == 'int':
                    attr = EventAttributeValueInt()
                elif eav.data_type == 'decimal':
                    attr = EventAttributeValueDecimal()
                elif eav.data_type == 'date':
                    attr = EventAttributeValueDate()
                else:
                    continue
                attr.attribute = eav
                attr.data_type =eav.data_type
                attr.event = event
                attr.value = a[key]
                attr.save()

        phenomena = []        
        if not phenomena_list:
            phenomenon_obj = {
                'begin_date': event.begin_date,
                'end_date': event.end_date,
                'administrative_division': event.country                
            }            
            phenomena_list = [phenomenon_obj]
        for p in phenomena_list:            
            p['event'] = event
            phenomenon = Phenomenon(**p)
            phenomenon.save()
            phenomenon.refresh_from_db()
            phenomena.append(phenomenon)

        return (event, phenomena)
    
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

    def insert_aggregate_values(self, sample_adm_div = None, adm_level_precision = 2):
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
    
    def insert_assessment_value(self, obj):
        if 'damage_assessment' in obj and 'phenomenon' in obj:
            for da in v['damage_assessment']:                        
                axis_x = DamageTypeValue.objects.filter(damage_assessment=da, axis='x')
                axis_y = DamageTypeValue.objects.filter(damage_assessment=da, axis='y')
                axis_z = DamageTypeValue.objects.filter(damage_assessment=da, axis='z')                        
                damage_value = v[str(v['dim1'])]

                da_value, created = DamageAssessmentValue.objects.get_or_create(
                    damage_assessment=da,
                    phenomenon=phenomenon,
                    damage_type_value_1=axis_x,
                    damage_type_value_2=axis_y,
                    damage_type_value_3=axis_z                            
                )
                to_update = {
                    'value': damage_value,
                    'item': v['item'] if 'item' in v else None,
                    'linked_item': v['linked_item'] if 'linked_item' in v else None,
                    'location': v['location'] if 'location' in v else None
                }                        
                da_value.objects.filter(pk=da_value.pk).update(**to_update)
    
    def insert_assessment_values(self, values):        
        if values:
            with transaction.atomic():
                for v in values:
                    self.insert_assessment_value(v)
                                    