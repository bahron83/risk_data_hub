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

import os
import StringIO

from django.conf import settings

from django.core.management import call_command
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django import forms
from django.forms import models
from django.forms import BaseInlineFormSet

from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from dateutil.parser import parse

from risks.models.event import Event, EventImport, EventImportDamage
from risks.models.eav_attribute import EavAttribute, data_types
from risks.models.region import Region
from risks.models.hazard_set import HazardSet, DamageAssessmentImportMetadata
from risks.models.risk_analysis import DamageAssessment, DamageAssessmentCreate, DamageAssessmentImportData
from risks.tasks import (create_damage_assessment, import_damage_assessment_data,
                            import_damage_assessment_metadata, import_event_data, import_event_attributes)


def is_valid_attribute(attribute, value):
    data_type = attribute.data_type
    if data_type == 'int':
        try:
            int(value)
        except ValueError:
            return False
    elif data_type == 'decimal':
        try:
            float(value)
        except ValueError:
            return False    
    elif data_type == 'date':
        try:
            parse(value)
        except ValueError:
            return False
    return True

class EventAttributeInlineFormSet(BaseInlineFormSet):        
    def __init__(self, *args, **kwargs): 
        data_type = None        
        for t in data_types:
            if t[0] in kwargs['prefix']:                    
                data_type = t[0]
                break
        if data_type:        
            event_attributes = Event.get_attributes(data_type)         
            if event_attributes:
                kwargs['initial'] = []            
                for a in event_attributes:
                    if a not in kwargs['queryset']:
                        kwargs['initial'].append({'attribute': a})                         
                        
        super(EventAttributeInlineFormSet, self).__init__(*args, **kwargs)

class PostEventPublishForm(forms.Form):
    title = 'Set state ready for selected events'
    state = forms.ChoiceField(choices=(('ready', 'ready'),))

class EventForm(forms.ModelForm):
    class Meta:
        model = Event                
        fields = '__all__'
        fields_order = ['begin_date','end_date']
        widgets = {
            # choose one mode from ['text', 'code', 'tree', 'form', 'view']
            'details': JSONEditorWidget(mode='form')
        }    

    def clean(self):
        details = self.cleaned_data.get('details')
        if details:
            for k in details.keys():
                try:
                    attribute = EavAttribute.objects.get(name=k)
                except EavAttribute.DoesNotExist:
                    raise form.ValidationError("Unknown attribute")
                if not is_valid_attribute(attribute, details[k]):
                    raise forms.ValidationError("Invalid data for attribute {}. Please, check that is a valid {}".format(k, attribute.data_type))
        return self.cleaned_data

class CreateDamageAssessmentForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = DamageAssessmentCreate
        fields = ("descriptor_file",)

    def clean_descriptor_file(self):
        file_ini = self.cleaned_data['descriptor_file']
        path = default_storage.save('tmp/'+file_ini.name,
                                    ContentFile(file_ini.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('descriptor_files', file_ini.name)
        
        try:
            create_damage_assessment(tmp_file, final_name, self.current_user.id)        
        except ValueError, e:
            raise forms.ValidationError(e)

        return file_ini        


class ImportDataDamageAssessmentForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = DamageAssessmentImportData
        fields = ('riskapp', 'region', 'damage_assessment', "data_file",)

    def __init__(self, *args, **kwargs):
        super(ImportDataDamageAssessmentForm, self).__init__(*args, **kwargs)        
        if not self.current_user.is_superuser:
            self.fields['region'].queryset = Region.objects.filter(
                                            owner=self.current_user)
            self.fields['damage_assessment'].queryset = DamageAssessment.objects.filter(
                                            owner=self.current_user)

    def clean_data_file(self):
        file_xlsx = self.cleaned_data['data_file']
        path = default_storage.save('tmp/'+file_xlsx.name,
                                    ContentFile(file_xlsx.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('data_files', file_xlsx.name)

        risk_app = self.cleaned_data['riskapp']
        region = self.cleaned_data['region']
        da = self.cleaned_data['damage_assessment']
        current_user = self.current_user   
                
        import_risk_data.delay(tmp_file, risk_app.name, da.name, region.name, final_name, current_user.id)        

        return file_xlsx


class ImportMetadataDamageAssessmentForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = DamageAssessmentImportMetadata
        fields = ('riskapp', 'region', 'damage_assessment', "metadata_file",)

    def __init__(self, *args, **kwargs):
        super(ImportMetadataDamageAssessmentForm, self).__init__(*args, **kwargs)        
        if not self.current_user.is_superuser:
            self.fields['region'].queryset = Region.objects.filter(
                                            owner=self.current_user)
            self.fields['damage_assessment'].queryset = DamageAssessment.objects.filter(
                                            owner=self.current_user)
    
    def clean_metadata_file(self):
        file_xlsx = self.cleaned_data['metadata_file']
        path = default_storage.save('tmp/'+file_xlsx.name,
                                    ContentFile(file_xlsx.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('metadata_files', file_xlsx.name)

        risk_app = self.cleaned_data['riskapp']
        region = self.cleaned_data['region']
        da = self.cleaned_data['damage_assessment']

        try:
            import_damage_assessment_metadata(tmp_file, risk_app.name, da.name, region.name, final_name)
        except ValueError, e:
            raise forms.ValidationError(e)

        return file_xlsx

class ImportDataEventForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = EventImport
        fields = ('riskapp', 'region', "data_file",)

    def __init__(self, *args, **kwargs):
        super(ImportDataEventForm, self).__init__(*args, **kwargs)        
        if not self.current_user.is_superuser:
            self.fields['region'].queryset = Region.objects.filter(
                                            owner=self.current_user)            

    def clean_data_file(self):
        file_xlsx = self.cleaned_data['data_file']
        path = default_storage.save('tmp/'+file_xlsx.name,
                                    ContentFile(file_xlsx.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('data_files', file_xlsx.name)

        risk_app = self.cleaned_data['riskapp']
        region = self.cleaned_data['region']     
        current_user = self.current_user   
        
        import_event_data.delay(tmp_file, risk_app.name, region.name, final_name, current_user.id)                    
        
        return file_xlsx

class ImportDataEventAttributeForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = EventImportDamage
        fields = ('riskapp', 'region', 'damage_assessment', "adm_level_precision", "data_file",) #allow_null_values checkbox not shown

    def __init__(self, *args, **kwargs):
        super(ImportDataEventAttributeForm, self).__init__(*args, **kwargs)        
        if not self.current_user.is_superuser:
            self.fields['region'].queryset = Region.objects.filter(
                                            owner=self.current_user)
            self.fields['damage_assessment'].queryset = DamageAssessment.objects.filter(
                                            owner=self.current_user)
    
    def clean_data_file(self):
        file_xlsx = self.cleaned_data['data_file']
        path = default_storage.save('tmp/'+file_xlsx.name,
                                    ContentFile(file_xlsx.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('data_files', file_xlsx.name)

        risk_app = self.cleaned_data['riskapp']
        region = self.cleaned_data['region']  
        da = self.cleaned_data['damage_assessment']
        allow_null_values = False#self.cleaned_data['allow_null_values']
        adm_level_precision = self.cleaned_data['adm_level_precision']
        current_user = self.current_user
                
        import_event_attributes.delay(tmp_file, risk_app.name, da.name, region.name, allow_null_values, final_name, current_user.id, adm_level_precision)        

        return file_xlsx
