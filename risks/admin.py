# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.db.models import Count

import nested_admin

# Register your models here.
from risks.models import (RiskApp, AnalysisType, AssetCategory, Asset, AssetItem, MarketValue, DamageType, DamageTypeValue,
                                DamageAssessment, DamageAssessmentValue, HazardSet, EavAttribute,
                                Event, Phenomenon, 
                                AttributeSet,
                                Hazard, AdministrativeDivision, Location, Region, PointOfContact,
                                Owner, SendaiTarget, SendaiIndicator, DamageAssessmentCreate, DamageAssessmentImportData,
                                DamageAssessmentImportMetadata, EventImport, EventImportDamage, DataProvider, DataProviderMappings)
from risks.forms import (EventAttributeInlineFormSet, CreateDamageAssessmentForm, ImportDataDamageAssessmentForm,
                            ImportMetadataDamageAssessmentForm, ImportDataEventForm, ImportDataEventAttributeForm, PostEventPublishForm,
                            EventForm)
from risks.helpers.event import EventHelper
from risks.const.messages import *

from django.core.management import call_command

from decorators import action_form

from risk_data_hub import local_settings


admin.site.site_header = 'Risk Data Hub - Administration'
admin.site.site_url = local_settings.SITEURL

'''class EventAttributeValueVarcharInline(admin.StackedInline):
    def get_extra(self, request, obj=None, **kwargs): 
        if obj is None:
            return 1       
        return obj.get_extra_inline('varchar')        
    
    model = EventAttributeValueVarchar    
    readonly_fields = ('data_type',)
    formset = EventAttributeInlineFormSet        
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(EventAttributeValueVarcharInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'attribute':
            field.queryset = field.queryset.filter(data_type='varchar')
        return field

class EventAttributeValueTextInline(admin.StackedInline):
    def get_extra(self, request, obj=None, **kwargs):        
        if obj is None:
            return 1       
        return obj.get_extra_inline('text')        
    
    model = EventAttributeValueText
    readonly_fields = ('data_type',)
    formset = EventAttributeInlineFormSet        
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(EventAttributeValueTextInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'attribute':
            field.queryset = field.queryset.filter(data_type='text')
        return field

class EventAttributeValueIntInline(admin.StackedInline):
    def get_extra(self, request, obj=None, **kwargs):        
        if obj is None:
            return 1       
        return obj.get_extra_inline('int')        
    
    model = EventAttributeValueInt
    readonly_fields = ('data_type',)
    formset = EventAttributeInlineFormSet        
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(EventAttributeValueIntInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'attribute':
            field.queryset = field.queryset.filter(data_type='int')
        return field

class EventAttributeValueDecimalInline(admin.StackedInline):
    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1               
        return obj.get_extra_inline('decimal')        
    
    model = EventAttributeValueDecimal
    readonly_fields = ('data_type',)
    formset = EventAttributeInlineFormSet        
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(EventAttributeValueDecimalInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'attribute':
            field.queryset = field.queryset.filter(data_type='decimal')
        return field

class EventAttributeValueDateInline(admin.StackedInline):
    def get_extra(self, request, obj=None, **kwargs): 
        if obj is None:
            return 1              
        return obj.get_extra_inline('date')        
    
    model = EventAttributeValueDate
    readonly_fields = ('data_type',)
    formset = EventAttributeInlineFormSet        
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(EventAttributeValueDateInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'attribute':
            field.queryset = field.queryset.filter(data_type='date')
        return field'''

class BaseAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseAdmin, self).get_form(request, obj, **kwargs)
        attribute_set = form.base_fields.pop('attribute_set')
        form.base_fields['attribute_set'] = attribute_set 
        details = form.base_fields.pop('details')
        form.base_fields['details'] = details 
        return form

class MarketValueInline(nested_admin.NestedStackedInline):
    model = MarketValue
    extra = 0

class AssetItemInline(nested_admin.NestedStackedInline):
    model = AssetItem
    extra = 1
    inlines = [MarketValueInline]

class SendaiIndicatorInline(admin.StackedInline):
    model = SendaiIndicator
    extra = 1

class DamageTypeValueInline(admin.TabularInline):
    model = DamageTypeValue
    extra = 2

class PhenomenonInline(admin.StackedInline):
    model = Phenomenon
    extra = 1

class AdministrativeDivisionAdmin(admin.ModelAdmin):
    model = AdministrativeDivision
    list_display_links = ('id',)
    list_display = ('id', 'code', 'name',)

class AnalysisTypeAdmin(admin.ModelAdmin):
    model = AnalysisType
    list_display_links = ('id',)
    list_display = ('id', 'name', 'title', 'scope',)

class AssetCategoryAdmin(admin.ModelAdmin):
    model = AssetCategory
    list_display_links = ('id',)
    list_display = ('id', 'name',)

class AssetAdmin(admin.ModelAdmin):
    model = Asset
    list_display_links = ('id',)
    list_display = ('id', 'name',)
    readonly_fields = ('entity_type',)
    inlines = [AssetItemInline]

class AttributeSetAdmin(admin.ModelAdmin):
    model = AttributeSet
    list_display_links = ('id',)
    list_display = ('id', 'name',)

class DamageTypeAdmin(admin.ModelAdmin):
    model = DamageType
    list_display_links = ('id',)
    list_display = ('id', 'name', 'abstract', 'unit',)
    inlines = [DamageTypeValueInline]

class DamageAssessmentAdmin(admin.ModelAdmin):
    model = DamageAssessment
    list_display_links = ('id',)
    list_display = ('id', 'name', 'analysis_type', 'unit_of_measure',)
    inlines = [DamageTypeValueInline]

class DamageAssessmentValueAdmin(admin.ModelAdmin):
    model = DamageAssessmentValue
    list_display_links = ('id',)
    list_display = ('id', 'damage_assessment', 'phenomenon', 'damage_type_value_1', 'damage_type_value_2', 'item', 'value',)    

class EavAttributeAdmin(admin.ModelAdmin):
    model = EavAttribute
    list_display_links = ('id',)
    list_display = ('id', 'code', 'name', 'entity_type',)

class EventAdmin(admin.ModelAdmin):
    model = Event
    list_display_links = ('id',)
    list_display = ('id', 'code', 'begin_date',)       
    search_fields = ('code',)
    readonly_fields = ('entity_type', 'code',)
    #inlines = [EventAttributeValueVarcharInline, EventAttributeValueTextInline, EventAttributeValueIntInline, EventAttributeValueDecimalInline, EventAttributeValueDateInline, PhenomenonInline]    
    inlines = [PhenomenonInline]
    actions = ['make_published'] 
    form = EventForm   

    '''def get_queryset(self, request):
        qs = super(EventAdmin, self).get_queryset(request).annotate(_risks_count=Count('risk_analysis')).order_by('_risks_count', 'iso2')      
        if request.user.is_superuser:
            return qs
        regions_owned = Region.objects.filter(owner=request.user)
        return qs.filter(region__in=regions_owned)
    '''

    #def has_add_permission(self, request):
    #    return False

    '''def risks_count(self, obj):        
        return obj._risks_count    

    risks_count.short_description = _("Number of Risk Analysis")
    risks_count.admin_order_field = '_risks_count'
    '''    

    def get_queryset(self, request):
        qs = super(EventAdmin, self).get_queryset(request)
        if 'change' in request.path:                        
            event_id = [s for s in request.path.split('/') if s.isdigit()]
            if event_id:
                event_id = int(str(event_id[0]))
                event_from_qs = qs.filter(pk=event_id).first()
                if event_from_qs:                
                    event_from_qs.sync_details_field()
        return qs        

    def get_fields(self, request, obj=None):
        if obj is None:
            return ['attribute_set']
        else:            
            return [attr.name for attr in obj._meta.get_fields() if not attr.auto_created and attr.name != 'id']
    
    def get_inline_instances(self, request, obj=None):        
        if obj is None:
            return []
        return super(EventAdmin, self).get_inline_instances(request, obj)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):            
            yield inline.get_formset(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['entity_type', 'code', 'state']
        if obj is not None:
            readonly_fields.append('attribute_set')
        return readonly_fields

    def response_add(self, request, obj, post_url_continue=None):
        Event.objects.filter(pk=obj.id).update(details=obj.get_initial_json_data())
        url = '/admin/{}/event/{}/change/'.format(self.model._meta.app_label, obj.id)
        return redirect(url)

    @action_form(PostEventPublishForm)
    def make_published(self, request, queryset, form):
        eh = EventHelper()        
        return eh.sync_geodb(queryset)
            
    make_published.short_description = 'Publish selected events'

class HazardAdmin(admin.ModelAdmin):
    model = Hazard
    list_display_links = ('id',)
    list_display = ('id', 'mnemonic', 'title',)

class HazardSetAdmin(admin.ModelAdmin):
    model = HazardSet
    list_display_links = ('id',)
    list_display = ('id', 'title', 'damage_assessment', 'date')

class LocationAdmin(admin.ModelAdmin):
    model = Location
    list_display_links = ('id',)
    list_display = ('id', 'location_type', 'address', 'lat', 'lon', 'administrative_division',)

class OwnerAdmin(admin.ModelAdmin):
    model = Owner
    list_display_links = ('id',)
    list_display = ('id', 'name',)

class PointOfContactAdmin(admin.ModelAdmin):
    model = PointOfContact
    list_display_links = ('id',)
    list_display = ('id', 'individual_name', 'organization_name', 'country',)

class RegionAdmin(admin.ModelAdmin):
    model = Region
    list_display_links = ('id',)
    list_display = ('id', 'name',)

class SendaiTargetAdmin(admin.ModelAdmin):
    model = SendaiTarget
    list_display_links = ('id',)
    list_display = ('id', 'name', 'description',)
    inlines = [SendaiIndicatorInline]

class DataProviderInlineAdmin(admin.StackedInline):
    model = DataProviderMappings
    extra = 1

class DataProviderAdmin(admin.ModelAdmin):
    model = DataProvider
    list_display = ('name',)
    list_display_links = ('name',) 
    inlines = [DataProviderInlineAdmin]       

@admin.register(RiskApp)
class RiskAppAdmin(admin.ModelAdmin):
    list_display = ('name',)

class DamageAssessmentCreateAdmin(admin.ModelAdmin):
    model = DamageAssessmentCreate    
    list_display = ('descriptor_file',)    
    form = CreateDamageAssessmentForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(DamageAssessmentCreateAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super(DamageAssessmentCreateAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def get_form(self, request, obj=None, **kwargs):
        form = super(DamageAssessmentCreateAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        qs = super(DamageAssessmentCreateAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        damage_assessment_owned_files = DamageAssessment.objects.filter(owner=request.user).values_list('descriptor_file', flat=True)
        return qs.filter(descriptor_file__in=damage_assessment_owned_files).distinct()

class DamageAssessmentImportDataAdmin(admin.ModelAdmin):
    model = DamageAssessmentImportData
    list_display = ('data_file', 'riskapp', 'region', 'damage_assessment',)
    form = ImportDataDamageAssessmentForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(DamageAssessmentImportDataAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super(DamageAssessmentImportDataAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def get_form(self, request, obj=None, **kwargs):
        form = super(DamageAssessmentImportDataAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        qs = super(DamageAssessmentImportDataAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        damage_assessment_owned = DamageAssessment.objects.filter(owner=request.user)
        return qs.filter(riskanalysis__in=damage_assessment_owned)

    def save_model(self, request, obj, form, change):
        messages.add_message(request, messages.INFO, FILE_UPLOADED_EMAIL)
        super(DamageAssessmentImportDataAdmin, self).save_model(request, obj, form, change)


class DamageAssessmentImportMetaDataAdmin(admin.ModelAdmin):
    model = DamageAssessmentImportData
    list_display = ('metadata_file', 'riskapp', 'region', 'damage_assessment',)
    form = ImportMetadataDamageAssessmentForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(DamageAssessmentImportMetaDataAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super(DamageAssessmentImportMetaDataAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def get_form(self, request, obj=None, **kwargs):
        form = super(DamageAssessmentImportMetaDataAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form   

    def get_queryset(self, request):
        qs = super(DamageAssessmentImportMetaDataAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        damage_assessment_owned = DamageAssessment.objects.filter(owner=request.user)
        return qs.filter(damage_assessment__in=damage_assessment_owned)

class EventImportAdmin(admin.ModelAdmin):
    model = EventImport
    list_display = ('data_file', 'riskapp', 'region')
    form = ImportDataEventForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(EventImportAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventImportAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def __init__(self, *args, **kwargs):
        super(EventImportAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def get_queryset(self, request):
        qs = super(EventImportAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        regions_owned = Region.objects.filter(owner=request.user)
        return qs.filter(region__in=regions_owned)

    def save_model(self, request, obj, form, change):
        messages.add_message(request, messages.INFO, FILE_UPLOADED_EMAIL)
        super(EventImportAdmin, self).save_model(request, obj, form, change)


class EventImportDamageDataAdmin(admin.ModelAdmin):
    model = EventImportDamage
    list_display = ('data_file', 'riskapp', 'region', 'damage_assessment', 'adm_level_precision')
    form = ImportDataEventAttributeForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(EventImportDamageDataAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventImportDamageDataAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def __init__(self, *args, **kwargs):
        super(EventImportDamageDataAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def get_queryset(self, request):
        qs = super(EventImportDamageDataAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        regions_owned = Region.objects.filter(owner=request.user)
        return qs.filter(region__in=regions_owned)

    def save_model(self, request, obj, form, change):
        messages.add_message(request, messages.INFO, FILE_UPLOADED_EMAIL)
        super(EventImportDamageDataAdmin, self).save_model(request, obj, form, change)


admin.site.register(AdministrativeDivision, AdministrativeDivisionAdmin)
admin.site.register(AnalysisType, AnalysisTypeAdmin)
admin.site.register(AssetCategory, AssetCategoryAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(AttributeSet, AttributeSetAdmin)
admin.site.register(DamageType, DamageTypeAdmin)
admin.site.register(DamageAssessment, DamageAssessmentAdmin)
admin.site.register(DamageAssessmentValue, DamageAssessmentValueAdmin)
admin.site.register(HazardSet, HazardSetAdmin)
admin.site.register(EavAttribute, EavAttributeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Hazard, HazardAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(PointOfContact, PointOfContactAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(SendaiTarget, SendaiTargetAdmin)
admin.site.register(DamageAssessmentCreate, DamageAssessmentCreateAdmin)
admin.site.register(DamageAssessmentImportData, DamageAssessmentImportDataAdmin)
admin.site.register(DamageAssessmentImportMetadata, DamageAssessmentImportMetaDataAdmin)
admin.site.register(EventImport, EventImportAdmin)
admin.site.register(EventImportDamage, EventImportDamageDataAdmin)