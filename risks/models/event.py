import re
from django.db import models
from geonode.layers.models import Layer
from risks.models import (HazardType, Region, AdministrativeDivision, RiskAnalysis, RiskApp,
                            RiskAppAware, LocationAware, HazardTypeAware, Exportable, Schedulable,
                            AdministrativeDivisionMappings)
from risks.models.base import rfs


class Event(RiskAppAware, LocationAware, HazardTypeAware, Exportable, Schedulable, models.Model):
    EXPORT_FIELDS = (('event_id', 'event_id',),                     
                     ('href', 'href',),)    

    event_id = models.CharField(max_length=25, primary_key=True)
    
    hazard_type = models.ForeignKey(
        HazardType,
        blank=False,
        null=False,
        unique=False,        
    )
    
    region = models.ForeignKey(
        Region,
        related_name='events',
        blank=False,
        null=False,
        unique=False,        
    )

    iso2 = models.CharField(max_length=10)
    nuts3 = models.CharField(max_length=255, null=True)
    begin_date = models.DateField()
    end_date = models.DateField()
    #loss_currency = models.CharField(max_length=3)
    #loss_amount = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    year = models.IntegerField()
    #loss_mln = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    event_type = models.CharField(max_length=50)
    event_source = models.CharField(max_length=255)
    #area_affected = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    #fatalities = models.CharField(max_length=10, null=True)
    #people_affected = models.IntegerField()
    cause = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    sources = models.CharField(max_length=255)

    administrative_divisions = models.ManyToManyField(
        'AdministrativeDivision',
        through='EventAdministrativeDivisionAssociation',
        related_name='event_adm',
    )

    further_administrative_divisions = models.ManyToManyField(
        'AdministrativeDivisionMappings',
        through='EventFurtherAdministrativeDivisionAssociation',
        related_name='event_further_adm',
    )

    '''layers = models.ManyToManyField(
        "Layer",
        through='EventLayerAssociation',
        related_name='event_layer',
    )'''
    related_layers = models.ManyToManyField(Layer, blank=True)  

    risk_analysis = models.ManyToManyField(
        'RiskAnalysis',
        through='EventRiskAnalysisAssociation'        
    )     
    
    class Meta:
        """
        """
        #ordering = ['iso2']
        db_table = 'risks_event'    
    

    def get_event_plain(self):
        #nuts3_adm_divs = AdministrativeDivision.objects.filter(level=2, code__in=self.nuts3.split(';'))
        nuts3_adm_divs = self.administrative_divisions.filter(level=2)
        nuts3_ids = nuts3_adm_divs.values_list('id', flat=True)        
        #nuts2_adm_divs = AdministrativeDivisionMappings.objects.filter(child__pk__in=nuts3_ids).order_by('name').distinct()        
        nuts2_adm_divs = self.further_administrative_divisions
        #nuts2_affected_names = AdministrativeDivisionMappings.objects.filter(child__pk__in=nuts3_ids).order_by('name').values_list('name', flat=True).distinct()        
        nuts3_affected_names = nuts3_adm_divs.values_list('name', flat=True)
        return {
            'event_id': self.event_id,
            'hazard_type': self.hazard_type.mnemonic,
            'hazard_title': self.hazard_type.title,
            'region': self.region.name,
            'iso2': self.iso2,
            'nuts2': ', '.join(nuts2_adm_divs.values_list('code', flat=True)),
            'nuts2_names': ', '.join(nuts2_adm_divs.values_list('name', flat=True)),
            'nuts3': self.nuts3,
            'nuts3_names': ', '.join(nuts3_affected_names),
            'begin_date': self.begin_date,
            'end_date': self.end_date,
            'year': self.year,
            'event_type': self.event_type,
            'event_source': self.event_source,            
            'cause': self.cause,
            'notes': self.notes,
            'sources': self.sources
        }

    def href(self):
        reg = self.get_region()
        loc = self.get_location()                
        return self.get_url('event', reg.name, loc.code, self.event_id)

    @staticmethod
    def generate_event_id(hazard_type, country, begin_date, region):
        suffix = 'R' if region.name != 'Europe' else ''
        pattern = r'^[A-Z]{4}[0-9]{12}' + re.escape(suffix) + r'$'
        events_to_check = Event.objects.filter(event_id__regex=pattern, hazard_type=hazard_type, year=begin_date.year)
        next_serial = 1
        duplicates = Event.objects.none()
        if events_to_check:           
            duplicates = events_to_check.filter(iso2=country.code, begin_date=begin_date)
            serials = [str(ev.event_id[-4:]) for ev in events_to_check]            
            serials.sort(reverse=True)
            next_serial = int(serials[0]) + 1        
        new_event_id = hazard_type.mnemonic + country.code + begin_date.strftime('%Y%m%d') + '{:>04d}'.format(next_serial) + suffix
        
        duplicates = duplicates.exclude(event_id=new_event_id).values_list('event_id', flat=True)
        return new_event_id, duplicates


class EventImportData(models.Model):
    data_file = models.FileField(upload_to='data_files', storage=rfs, max_length=255)

    # Relationships
    riskapp = models.ForeignKey(
        RiskApp,
        blank=False,
        null=False,
        unique=False,
    )

    region = models.ForeignKey(
        Region,
        blank=False,
        null=False,
        unique=False,
    )

    '''hazardtype = models.ForeignKey(
        HazardType,
        blank=False,
        null=False,
        unique=False,
    )'''

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
        ordering = ['riskapp', 'region']
        db_table = 'risks_data_event_files'
        verbose_name = 'Events: Import Data (Main) from XLSX file'
        verbose_name_plural = 'Events: Import Data (Main) from XLSX file'      

    def __unicode__(self):
        return u"{0}".format(self.data_file.name)


class EventImportAttributes(models.Model):
    data_file = models.FileField(upload_to='data_files', storage=rfs, max_length=255)

    # Relationships
    riskapp = models.ForeignKey(
        RiskApp,
        blank=False,
        null=False,
        unique=False,
    )

    region = models.ForeignKey(
        Region,
        blank=False,
        null=False,
        unique=False,
    )

    riskanalysis = models.ForeignKey(
        RiskAnalysis,
        blank=False,
        null=False,
        unique=False,
    )

    allow_null_values = models.BooleanField(default=False)

    adm_level_precision = models.CharField(max_length=10,
                                    choices=(("1", "Country"), ("2", "Nuts3")),
                                    default="1")

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
        ordering = ['riskapp', 'region', 'riskanalysis', 'adm_level_precision']
        db_table = 'risks_attribute_event_files'
        verbose_name = 'Risks Analysis: Import Events Data (Attributes) from XLSX file'
        verbose_name_plural = 'Risks Analysis: Import Events Data (Atributes) from XLSX file'      

    def __unicode__(self):
        return u"{0}".format(self.data_file.name)


###RELATIONS###
class EventAdministrativeDivisionAssociation(models.Model):
    id = models.AutoField(primary_key=True)
    
    #Relationships
    event = models.ForeignKey(
        Event,        
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )    
    adm = models.ForeignKey(
        AdministrativeDivision,        
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )          

    def __unicode__(self):
        return u"{0}".format(self.event.event_id + " - " +
                             self.adm.name)

    class Meta:
        """
        """
        db_table = 'risks_eventadministrativedivisionassociation'

class EventFurtherAdministrativeDivisionAssociation(models.Model):
    id = models.AutoField(primary_key=True)
    
    #Relationships
    event = models.ForeignKey(
        Event,        
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )    
    f_adm = models.ForeignKey(
        AdministrativeDivisionMappings,        
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )          

    def __unicode__(self):
        return u"{0}".format(self.event.event_id + " - " +
                             self.f_adm.name)

    class Meta:
        """
        """
        db_table = 'risks_eventfurtheradministrativedivisionassociation'

class EventRiskAnalysisAssociation(models.Model):
    id = models.AutoField(primary_key=True)
        
    event = models.ForeignKey(
        Event,        
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )    
    risk = models.ForeignKey(
        RiskAnalysis,        
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )          

    def __unicode__(self):
        return u"{0}".format(self.event.event_id + " - " +
                             self.risk.name)

    class Meta:
        """
        """
        db_table = 'risks_eventriskanalysisassociation'