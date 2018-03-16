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

from django.contrib import admin

from risks.models import RiskAnalysis
from risks.models import Region, AdministrativeDivision
from risks.models import AnalysisType, HazardType, DymensionInfo
from risks.models import PointOfContact, HazardSet
from risks.models import FurtherResource
from risks.models import AnalysisTypeFurtherResourceAssociation
from risks.models import DymensionInfoFurtherResourceAssociation
from risks.models import HazardSetFurtherResourceAssociation

from risks.models import RiskAnalysisCreate
from risks.models import RiskAnalysisImportData
from risks.models import RiskAnalysisImportMetadata
from risks.models import EventImportData
from risks.models import RiskApp
from risks.models import AdditionalData
from risks.models import Event
from risks.models import EventImportAttributes
from risks.models import AnalysisClass

from risks.forms import CreateRiskAnalysisForm
from risks.forms import ImportDataRiskAnalysisForm
from risks.forms import ImportMetadataRiskAnalysisForm
from risks.forms import ImportDataEventForm
from risks.forms import ImportDataEventAttributeForm


class DymensionInfoInline(admin.TabularInline):
    model = DymensionInfo.risks_analysis.through
    raw_id_fields = ('resource',)
    extra = 3


class AdministrativeDivisionInline(admin.StackedInline):
    model = AdministrativeDivision.risks_analysis.through
    exclude = ['geom', 'srid']
    extra = 3


class FurtherResourceInline(admin.TabularInline):
    model = AnalysisTypeFurtherResourceAssociation
    raw_id_fields = ('resource',)
    extra = 3


class LinkedResourceInline(admin.TabularInline):
    model = DymensionInfoFurtherResourceAssociation
    raw_id_fields = ('resource',)
    extra = 3


class AdditionalResourceInline(admin.TabularInline):
    model = HazardSetFurtherResourceAssociation
    raw_id_fields = ('resource',)
    extra = 3


class FurtherResourceAdmin(admin.ModelAdmin):
    model = FurtherResource
    list_display_links = ('resource',)
    list_display = ('resource',)
    group_fieldsets = True


class RegionAdmin(admin.ModelAdmin):
    model = Region
    list_display_links = ('name',)
    list_display = ('name', 'level')
    search_fields = ('name',)
    readonly_fields = ('administrative_divisions',)
    inlines = [FurtherResourceInline]
    group_fieldsets = True


class AdministrativeDivisionAdmin(admin.ModelAdmin):
    model = AdministrativeDivision
    list_display_links = ('name',)
    list_display = ('code', 'name', 'parent')
    search_fields = ('code', 'name',)
    readonly_fields = ('risks_analysis',)
    # inlines = [AdministrativeDivisionInline]
    group_fieldsets = True


class AnalysisTypeAdmin(admin.ModelAdmin):
    model = AnalysisType
    list_display_links = ('name',)
    list_display = ('name', 'title', 'description', 'analysis_class', 'app',)
    search_fields = ('name', 'title',)
    list_filter = ('app__name', 'analysis_class__name',)
    inlines = [FurtherResourceInline]
    group_fieldsets = True


class HazardTypeAdmin(admin.ModelAdmin):
    model = HazardType
    list_display_links = ('mnemonic',)
    list_display = ('mnemonic', 'gn_description', 'title', 'app',)
    search_fields = ('mnemonic', 'gn_description', 'title',)
    list_filter = ('mnemonic', 'app__name',)
    inlines = [FurtherResourceInline]
    list_select_related = True
    group_fieldsets = True


class DymensionInfoAdmin(admin.ModelAdmin):
    model = DymensionInfo
    list_display_links = ('name',)
    list_display = ('name', 'unit', 'abstract',)
    search_fields = ('name',)
    filter_vertical = ('risks_analysis',)
    inlines = [LinkedResourceInline, DymensionInfoInline]
    group_fieldsets = True


class RiskAnalysisAdmin(admin.ModelAdmin):
    model = RiskAnalysis
    list_display_links = ('name',)
    list_display = ('name', 'state', 'app')
    search_fields = ('name',)
    list_filter = ('state', 'hazard_type', 'analysis_type', 'app__name',)
    readonly_fields = ('administrative_divisions', 'descriptor_file', 'data_file', 'metadata_file', 'state',)
    # inlines = [AdministrativeDivisionInline, DymensionInfoInline]
    inlines = [LinkedResourceInline, DymensionInfoInline]
    group_fieldsets = True
    raw_id_fields = ('hazardset', 'layer', 'style', 'reference_layer', 'reference_style',)
    filter_horizontal = ('additional_layers',)

    def has_add_permission(self, request):
        return False


class PointOfContactAdmin(admin.ModelAdmin):
    model = PointOfContact
    list_display_links = ('individual_name', 'organization_name',)
    list_display = ('individual_name', 'organization_name',)
    search_fields = ('individual_name', 'organization_name',)
    group_fieldsets = True


class HazardSetAdmin(admin.ModelAdmin):
    model = HazardSet
    list_display_links = ('title',)
    list_display = ('title',)
    search_fields = ('title', 'riskanalysis', 'country',)
    inlines = [AdditionalResourceInline]
    group_fieldsets = True

    def has_add_permission(self, request):
        return False


class RiskAnalysisCreateAdmin(admin.ModelAdmin):
    model = RiskAnalysisCreate
    list_display = ('descriptor_file', )
    form = CreateRiskAnalysisForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(RiskAnalysisCreateAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super(RiskAnalysisCreateAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


class RiskAnalysisImportDataAdmin(admin.ModelAdmin):
    model = RiskAnalysisImportData
    list_display = ('data_file', 'riskapp', 'region', 'riskanalysis',)
    form = ImportDataRiskAnalysisForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(RiskAnalysisImportDataAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super(RiskAnalysisImportDataAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


class RiskAnalysisImportMetaDataAdmin(admin.ModelAdmin):
    model = RiskAnalysisImportMetadata
    list_display = ('metadata_file', 'riskapp', 'region', 'riskanalysis',)
    form = ImportMetadataRiskAnalysisForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(RiskAnalysisImportMetaDataAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super(RiskAnalysisImportMetaDataAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


class EventAdmin(admin.ModelAdmin):
    model= Event
    list_display_links = ('event_id',)
    list_display = ('event_id', 'iso2', 'nuts3', 'begin_date', 'end_date',)
    search_fields = ('event_id',)
    list_filter = ('iso2', 'year',) 
    readonly_fields = ('administrative_divisions',)
    group_fieldsets = True  
    list_select_related = True
    filter_horizontal = ('related_layers',)

class EventImportDataAdmin(admin.ModelAdmin):
    model = EventImportData
    list_display = ('data_file', 'riskapp', 'region')
    form = ImportDataEventForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(EventImportDataAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super(EventImportDataAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

class EventImportAttributeDataAdmin(admin.ModelAdmin):
    model = EventImportAttributes
    list_display = ('data_file', 'riskapp', 'region', 'riskanalysis')
    form = ImportDataEventAttributeForm
    group_fieldsets = True

    def get_actions(self, request):
        actions = super(EventImportAttributeDataAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super(EventImportAttributeDataAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

class AnalysisClassAdmin(admin.ModelAdmin):
    model = AnalysisClass
    list_display = ('name', 'title',)
    list_display_links = ('name',)


@admin.register(RiskApp)
class RiskAppAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(AdditionalData)
class AdditionalDataAdmin(admin.ModelAdmin):
    list_display = ('risk_analysis', 'name',)
    raw_id_fields = ('risk_analysis',)


admin.site.register(Region, RegionAdmin)
admin.site.register(AdministrativeDivision, AdministrativeDivisionAdmin)
admin.site.register(AnalysisType, AnalysisTypeAdmin)
admin.site.register(HazardType, HazardTypeAdmin)
admin.site.register(DymensionInfo, DymensionInfoAdmin)
admin.site.register(RiskAnalysis, RiskAnalysisAdmin)
admin.site.register(PointOfContact, PointOfContactAdmin)
admin.site.register(HazardSet, HazardSetAdmin)
admin.site.register(FurtherResource, FurtherResourceAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(AnalysisClass, AnalysisClassAdmin)

admin.site.register(RiskAnalysisCreate, RiskAnalysisCreateAdmin)
admin.site.register(RiskAnalysisImportData, RiskAnalysisImportDataAdmin)
admin.site.register(RiskAnalysisImportMetadata, RiskAnalysisImportMetaDataAdmin)
admin.site.register(EventImportData, EventImportDataAdmin)
admin.site.register(EventImportAttributes, EventImportAttributeDataAdmin)
