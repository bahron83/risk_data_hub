# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.db.models import Count
from geonode.people.admin import ProfileAdmin

import nested_admin

# Register your models here.
from risks.models import (RiskApp, AnalysisType, AssetCategory, Asset, AssetItem, MarketValue, DamageType, DamageTypeValue,
                                DamageAssessment, HazardSet, EavAttribute, FurtherResource,
                                Event, Phenomenon, Style,
                                AttributeSet,
                                Hazard, AdministrativeDivision, Location, Region, PointOfContact,
                                Owner, SendaiTarget, SendaiIndicator, DamageAssessmentCreate, DamageAssessmentImportData,
                                DamageAssessmentImportMetadata, EventImportData, DataProvider, DataProviderMappings, RdhUser, AccessRule)
from risks.forms import (EventAttributeInlineFormSet, CreateDamageAssessmentForm, ImportDataDamageAssessmentForm,
                            ImportMetadataDamageAssessmentForm, ImportDataEventForm, PostEventPublishForm,
                            EventForm, StyleForm)
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
    raw_id_fields = ('resource',)
    extra = 2

class PhenomenonInline(admin.StackedInline):
    model = Phenomenon
    extra = 1

class AdministrativeDivisionAdmin(admin.ModelAdmin):
    model = AdministrativeDivision
    list_display_links = ('id',)
    list_display = ('id', 'code', 'name',)
    search_fields = ('code', 'name',)

class AnalysisTypeAdmin(admin.ModelAdmin):
    model = AnalysisType
    list_display_links = ('id',)
    list_display = ('id', 'name', 'title',)

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
    readonly_fields = ('administrative_divisions', 'descriptor_file', 'data_file', 'metadata_file', 'state',)
    inlines = [DamageTypeValueInline]

    def has_add_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        fields = list(super(DamageAssessmentAdmin, self).get_fields(request, obj))
        exclude_set = set()
        if obj:  # obj will be None on the add page, and something on change pages
            exclude_set.add('values')
        return [f for f in fields if f not in exclude_set]

'''class DamageAssessmentValueAdmin(admin.ModelAdmin):
    model = DamageAssessmentValue
    list_display_links = ('id',)
    list_display = ('id', 'damage_assessment', 'phenomenon', 'damage_type_value_1', 'damage_type_value_2', 'item', 'value',)

    def has_add_permission(self, request, obj=None):
        return False'''    

class StyleAdmin(admin.ModelAdmin):
    model = Style
    form = StyleForm
    list_display_links = ('id',)
    list_display = ('id', 'name',)

    def get_queryset(self, request):
        qs = super(StyleAdmin, self).get_queryset(request)
        if 'change' in request.path:                        
            style_id = [s for s in request.path.split('/') if s.isdigit()]
            if style_id:
                style_id = int(str(style_id[0]))
                style_from_qs = qs.filter(pk=style_id).first()
                if style_from_qs:                
                    style_from_qs.sync_details_field()
        return qs 

    def get_form(self, request, obj=None, **kwargs):
        form = super(StyleAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['content'].initial = StyleForm.json_schema
        return form

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

class FurtherResourceAdmin(admin.ModelAdmin):
    model = FurtherResource
    list_display_links = ('resource',)
    list_display = ('resource',)
    group_fieldsets = True  

    def get_form(self, request, obj=None, **kwargs):
        form = super(FurtherResourceAdmin, self).get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['resource'].queryset = form.base_fields['resource'].queryset.filter(owner=request.user)
        return form

    def get_queryset(self, request):
        qs = super(FurtherResourceAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

class HazardAdmin(admin.ModelAdmin):
    model = Hazard
    list_display_links = ('id',)
    list_display = ('id', 'mnemonic', 'title',)
    readonly_fields = ('state',)

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

class DataProviderMappingsAdmin(admin.ModelAdmin):
    model = DataProviderMappings    
    list_display = ('data_provider', 'hazard', 'order',)
    list_filter = ('hazard',)

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

class EventImportDataAdmin(admin.ModelAdmin):
    model = EventImportData
    list_display = ('data_file', 'riskapp', 'region', 'damage_assessment')
    form = ImportDataEventForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(EventImportDataAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventImportDataAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def __init__(self, *args, **kwargs):
        super(EventImportDataAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def get_queryset(self, request):
        qs = super(EventImportDataAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.region:
            return qs.filter(region=request.user.region)
        return None

    def save_model(self, request, obj, form, change):
        messages.add_message(request, messages.INFO, FILE_UPLOADED_EMAIL)
        super(EventImportDataAdmin, self).save_model(request, obj, form, change)

class RdhUserAdmin(ProfileAdmin):     
    def is_user_in_group(self, user, group_name):
        return group_name in [str(g.name) for g in user.groups.all()]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(RdhUserAdmin, self).get_fieldsets(request, obj)
        if 'change' in request.path:
            user_groups_names = [str(g.name) for g in request.user.groups.all()]
            t1 = (None, {'fields': ('username', 'password')})            
            t4 = (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')})
            if not request.user.is_superuser:
                t4 = (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups')})
                if 'administrator' not in user_groups_names and request.user != obj:            
                    t1 = (None, {'fields': ['username']})                
            fieldsets = (
                t1,
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Region'), {'fields': ['region']}),
                t4,        
                (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                (_('Extended profile'), {'fields': ('organization', 'profile',
                                                    'position', 'voice', 'fax',
                                                    'delivery', 'city', 'area',
                                                    'zipcode', 'country',
                                                    'keywords')}),
            )
        return fieldsets
    
    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser or self.is_user_in_group(request.user, 'administrator'):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or self.is_user_in_group(request.user, 'administrator'):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        elif 'change' not in request.path:
            return True
        elif obj:
            if request.user == obj:
                return True
            elif request.user.region and obj.region == request.user.region:                
                if self.is_user_in_group(request.user, 'administrator'):
                    if not self.is_user_in_group(obj, 'administrator') and not obj.is_superuser:
                        return True
        return False

    def get_queryset(self, request):
        qs = super(RdhUserAdmin, self).get_queryset(request)
        if not request.user.is_superuser and 'change' not in request.path:            
            if request.user.region:
                return qs.filter(region=request.user.region, is_superuser=False)
        return qs  

    def response_add(self, request, obj, post_url_continue=None):
        obj.region = request.user.region
        obj.save()
        return super(RdhUserAdmin, self).response_add(request, obj, post_url_continue)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['region']
        return []

class AccessRuleAdmin(admin.ModelAdmin):
    model = AccessRule
    list_display = ('order', 'region', 'scope', 'damage_assessment', 'group', 'user', 'access',)
    #readonly_fields = ['region']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):   
        if db_field.name == 'region':
            kwargs['queryset'] = db_field.related_model.objects.filter(pk=request.user.region.pk)
            kwargs['initial'] = request.user.region.pk
        if db_field.name == 'damage_assessment':
            kwargs['queryset'] = db_field.related_model.objects.filter(region=request.user.region)
        if db_field.name == 'user':
            kwargs['queryset'] = db_field.related_model.objects.filter(region=request.user.region)
        return super(AccessRuleAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def response_add(self, request, obj, post_url_continue=None):
        obj.order = AccessRule.objects.all().count() - 1
        obj.save()
        return super(AccessRuleAdmin, self).response_add(request, obj, post_url_continue)  

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj is not None:
            readonly_fields.extend(['region', 'order'])
        return readonly_fields  


admin.site.register(AdministrativeDivision, AdministrativeDivisionAdmin)
admin.site.register(AnalysisType, AnalysisTypeAdmin)
admin.site.register(AssetCategory, AssetCategoryAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(AttributeSet, AttributeSetAdmin)
admin.site.register(DamageType, DamageTypeAdmin)
admin.site.register(DamageAssessment, DamageAssessmentAdmin)
#admin.site.register(DamageAssessmentValue, DamageAssessmentValueAdmin)
admin.site.register(DataProvider, DataProviderAdmin)
admin.site.register(DataProviderMappings, DataProviderMappingsAdmin)
admin.site.register(HazardSet, HazardSetAdmin)
admin.site.register(EavAttribute, EavAttributeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(FurtherResource, FurtherResourceAdmin)
admin.site.register(Hazard, HazardAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(PointOfContact, PointOfContactAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(SendaiTarget, SendaiTargetAdmin)
admin.site.register(DamageAssessmentCreate, DamageAssessmentCreateAdmin)
admin.site.register(DamageAssessmentImportData, DamageAssessmentImportDataAdmin)
admin.site.register(DamageAssessmentImportMetadata, DamageAssessmentImportMetaDataAdmin)
admin.site.register(EventImportData, EventImportDataAdmin)
admin.site.register(RdhUser, RdhUserAdmin)
admin.site.register(AccessRule, AccessRuleAdmin)
admin.site.register(Style, StyleAdmin)