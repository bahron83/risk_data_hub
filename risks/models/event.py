import datetime
import time
from datetime import timedelta
import re
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from geonode.layers.models import Layer
from risks.models.risk_app import RiskAppAware
from risks.models.entity import LocationAware, HazardTypeAware, Exportable, Schedulable
from risks.models import (EntityAbstract, AdministrativeDivision)
from risks.models.eav_attribute import entity_types
from risks.models.location import levels


DEFAULT_ENTITY_TYPE = 'event'

'''class EventAttributeValueVarchar(AttributeValueVarchar):    
    event = models.ForeignKey('Event')    

class EventAttributeValueText(AttributeValueText):    
    event = models.ForeignKey('Event')    

class EventAttributeValueInt(AttributeValueInt):    
    event = models.ForeignKey('Event')    

class EventAttributeValueDecimal(AttributeValueDecimal):    
    event = models.ForeignKey('Event')    

class EventAttributeValueDate(AttributeValueDate):    
    event = models.ForeignKey('Event')'''   

class Phenomenon(Exportable, models.Model):
    EXPORT_FIELDS = (
        ('id', 'id'),
        ('begin_date', 'begin_date'),
        ('end_date', 'end_date'),                        
        ('event_id', 'pevent_id'),
    )

    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        'Event',
        related_name='phenomena',
        on_delete=models.CASCADE
    )
    administrative_division = models.ForeignKey(
        'AdministrativeDivision',
        limit_choices_to={'id__in': AdministrativeDivision.objects.filter(level__gte=1)}
    )
    begin_date = models.DateField() 
    end_date = models.DateField()          

    class Meta:
        verbose_name_plural = 'Phenomena'

    def __unicode__(self):
        return u"id: {0} - date: {1} - location: {2}".format(self.event.code, self.begin_date, self.administrative_division.code)

    @property
    def padministrative_division(self):
        adm = self.administrative_division
        return adm.export(adm.EXPORT_FIELDS_ANALYSIS)    

    @property
    def pevent_id(self):
        return self.event.pk    

class Event(EntityAbstract, RiskAppAware, LocationAware, HazardTypeAware, Exportable, Schedulable):                
    EXPORT_FIELDS = (
        ('id', 'id'),
        ('code', 'code'),
        ('year', 'year'),
        ('begin_date', 'begin_date'),
        ('end_date', 'end_date'),
        ('country', 'pcountry'),        
    )
    
    id = models.AutoField(primary_key=True)    
    entity_type = models.CharField(max_length=20, null=False, choices=entity_types, default=DEFAULT_ENTITY_TYPE)        
    code = models.CharField(max_length=25, null=True, blank=True, db_index=True)    
    year = models.IntegerField(db_index=True, null=True, blank=True)
    begin_date = models.DateField(null=True, blank=True)       
    end_date = models.DateField(null=True, blank=True)    
    
    country = models.ForeignKey(
        'AdministrativeDivision',
        limit_choices_to={'id__in': AdministrativeDivision.objects.filter(level=1)},
        blank=True,
        null=True,
        unique=False,        
    )
    hazard_type = models.ForeignKey(
        'Hazard',
        blank=True,
        null=True,
        unique=False,        
    )
    region = models.ForeignKey(
        'Region',
        blank=True,
        null=True,
        unique=False,        
    )  
    related_layers = models.ManyToManyField(Layer, blank=True)  

    class Meta:
        """
        """        
        db_table = 'risks_event' 
        indexes = [
            GinIndex(
                fields=['details'],
                name='event_detail_gin',
            ),
        ]         

    def __unicode__(self):
        return u"Event ID {0}".format(self.id)    

    def get_phenomena(self):
        return Phenomenon.objects.filter(event=self)    

    def sync_details_field(self):
        details = {}
        if self.details:
            details = dict(self.details)
        for attr in self.get_attributes():            
            if attr.name not in details.keys():
                details[attr.name] = ''
        Event.objects.filter(pk=self.id).update(details=details)

    @property
    def phazard_type(self):
        return self.hazard_type.mnemonic

    @property
    def pcountry(self):
        return self.country.code
    
    @property
    def pregion(self):
        return self.region.name
    
    @staticmethod
    def get_fields_basic():
        return ['entity_type','code','year','begin_date','end_date','country','hazard_type','region']  
    
    def custom_export(self):
        phenomena = self.get_phenomena()
        phenomena_exp = [p.export() for p in phenomena]
        nuts2_adm_divs = [p.administrative_division for p in phenomena if p.administrative_division.level==levels.index('nuts2')]                
        nuts3_adm_divs = [p.administrative_division for p in phenomena if p.administrative_division.level==levels.index('nuts3')]
        if not nuts2_adm_divs:
            if nuts3_adm_divs:
                nuts2_adm_divs = list(set([adm.parent for adm in nuts3_adm_divs]))
        timestamp = int(time.mktime(self.begin_date.timetuple())) * 1000 if int(self.year) > 1900 else None

        obj = {
            'id': self.id,
            'code': self.code,
            'hazard_type': self.hazard_type.mnemonic,
            'hazard_title': self.hazard_type.title,
            'region': self.region.name,
            'iso2': self.country.code,
            'nuts2': ','.join([adm.code for adm in nuts2_adm_divs]),
            'nuts2_names': ', '.join([adm.name for adm in nuts2_adm_divs]),
            'nuts3': ','.join([adm.code for adm in nuts3_adm_divs]),
            'nuts3_names': ', '.join([adm.name for adm in nuts3_adm_divs]),
            'begin_date': self.begin_date,
            'end_date': self.end_date,
            'year': self.begin_date.year,
            'phenomena': phenomena_exp,
            'timestamp': timestamp
        }

        if self.details:
            for key, value in self.details.iteritems():
                obj[key] = value
        
        return obj
        

    def href(self):
        reg = self.get_region()
        loc = self.get_location()                
        return self.get_url('event', reg.name, loc.code, self.id)

    @staticmethod
    def generate_event_code(hazard_type, country, begin_date, region, draft=False):        
        suffix = 'R' if region.name != 'Europe' else ''        
        pattern = r'^[A-Z]{4}[0-9]{12}' + re.escape(suffix) + r'$'
        events_to_check = Event.objects.filter(code__regex=pattern, hazard_type=hazard_type, year=begin_date.year)
        next_serial = 1
        duplicates = Event.objects.none()
        if events_to_check:           
            duplicates = events_to_check.filter(country=country, begin_date=begin_date)
            serials = [str(ev.code[-4:]) for ev in events_to_check]            
            serials.sort(reverse=True)
            next_serial = int(serials[0]) + 1        
        new_code = hazard_type.mnemonic + country.code + begin_date.strftime('%Y%m%d') + '{:>04d}'.format(next_serial) + suffix
        
        duplicates = duplicates.exclude(code=new_code).values_list('code', flat=True)
        return new_code, duplicates

    @staticmethod
    def find_matches(obj):
        if obj['region'] and obj['hazard_type']:
            matches = Event.objects.filter(region=obj['region'], hazard_type=obj['hazard_type'])
            if 'country' in obj:                                
                matches = matches.filter(country=obj['country'])
            if 'year' in obj:                
                matches = matches.filter(year=obj['year'])
            if 'begin_date' in obj:
                lt_date = obj['begin_date'] + timedelta(days=7)
                gt_date = obj['begin_date'] - timedelta(days=7)
                matches = matches.filter(begin_date__gt=gt_date, begin_date__lt=lt_date)
            if 'sources' in obj:
                matches = matches.filter(sources=obj['sources'])
            return matches
        return None

    @staticmethod
    def find_exact_match(obj):
        temp_matches = Event.find_matches(obj)
        if 'begin_date' in obj:
            temp_matches = temp_matches.filter(begin_date=obj['begin_date'])
        if 'end_date' in obj:
            temp_matches = temp_matches.filter(begin_date=obj['begin_date'])
        if 'state' in obj:
            temp_matches = temp_matches.filter(state=obj['state'])
        return temp_matches.first()

    def has_exact_match(self):
        return Event.objects.filter(
            region=self.region,
            hazard_type=self.hazard_type,
            country=self.country,
            begin_date=self.begin_date,
            end_date=self.end_date).exists()

    def get_attributes_saved(self):
        attributes_saved = []
        attributes_saved += EventAttributeValueVarchar.objects.filter(event=self)
        attributes_saved += EventAttributeValueText.objects.filter(event=self)
        attributes_saved += EventAttributeValueInt.objects.filter(event=self)
        attributes_saved += EventAttributeValueDecimal.objects.filter(event=self)
        attributes_saved += EventAttributeValueDate.objects.filter(event=self)
        return attributes_saved
    
    def get_extra_inline(self, data_type = None):
        attributes_saved = self.get_attributes_saved()
        return len(Event.get_attributes(data_type)) - len(attributes_saved)

class EventImportData(models.Model):
    data_file = models.FileField(upload_to='data_files', max_length=255)

    # Relationships
    riskapp = models.ForeignKey(
        'RiskApp',
        blank=False,
        null=False,
        unique=False,
    )

    region = models.ForeignKey(
        'Region',
        blank=False,
        null=False,
        unique=False,
    )

    damage_assessment = models.ForeignKey(
        'DamageAssessment',
        blank=False,
        null=False,
        unique=False,
    )    

    def file_link(self):
        if self.data_file:
            return "<a href='%s'>download</a>" % (self.data_file.url,)
        else:
            return "No attachment"

    file_link.allow_tags = True

    def __unicode__(self):
        return u"{0}".format(self.data_file.name)

    class Meta:
        """
        """
        ordering = ['riskapp', 'region', 'damage_assessment']
        db_table = 'risks_event_data_files'
        verbose_name = 'Damage Assessment: Import Events Data from XLSX file'
        verbose_name_plural = 'Damage Assessment: Import Events Data from XLSX file'      

    def __unicode__(self):
        return u"{0}".format(self.data_file.name)
