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

from risks.models import Region
from risks.models import HazardSet
from risks.models import RiskAnalysis
from risks.models import RiskAnalysisCreate
from risks.models import RiskAnalysisImportData
from risks.models import RiskAnalysisImportMetadata
from risks.models import EventImportData
from risks.models import EventImportAttributes
from risks.tasks import create_risk_analysis, import_risk_data, import_risk_metadata, import_event_data, import_event_attributes


class CreateRiskAnalysisForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = RiskAnalysisCreate
        fields = ("descriptor_file",)

    def clean_descriptor_file(self):
        file_ini = self.cleaned_data['descriptor_file']
        path = default_storage.save('tmp/'+file_ini.name,
                                    ContentFile(file_ini.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('descriptor_files', file_ini.name)
        
        try:
            create_risk_analysis(tmp_file, final_name, self.current_user.id)        
        except ValueError, e:
            raise forms.ValidationError(e)

        return file_ini        


class ImportDataRiskAnalysisForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = RiskAnalysisImportData
        fields = ('riskapp', 'region', 'riskanalysis', "data_file",)

    def __init__(self, *args, **kwargs):
        super(ImportDataRiskAnalysisForm, self).__init__(*args, **kwargs)        
        if not self.current_user.is_superuser:
            self.fields['region'].queryset = Region.objects.filter(
                                            owner=self.current_user)
            self.fields['riskanalysis'].queryset = RiskAnalysis.objects.filter(
                                            owner=self.current_user)

    def clean_data_file(self):
        file_xlsx = self.cleaned_data['data_file']
        path = default_storage.save('tmp/'+file_xlsx.name,
                                    ContentFile(file_xlsx.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('data_files', file_xlsx.name)

        risk_app = self.cleaned_data['riskapp']
        region = self.cleaned_data['region']
        risk = self.cleaned_data['riskanalysis']
        current_user = self.current_user   
                
        import_risk_data.delay(tmp_file, risk_app.name, risk.name, region.name, final_name, current_user.id)        

        return file_xlsx


class ImportMetadataRiskAnalysisForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = RiskAnalysisImportMetadata
        fields = ('riskapp', 'region', 'riskanalysis', "metadata_file",)

    def __init__(self, *args, **kwargs):
        super(ImportMetadataRiskAnalysisForm, self).__init__(*args, **kwargs)        
        if not self.current_user.is_superuser:
            self.fields['region'].queryset = Region.objects.filter(
                                            owner=self.current_user)
            self.fields['riskanalysis'].queryset = RiskAnalysis.objects.filter(
                                            owner=self.current_user)
    
    def clean_metadata_file(self):
        file_xlsx = self.cleaned_data['metadata_file']
        path = default_storage.save('tmp/'+file_xlsx.name,
                                    ContentFile(file_xlsx.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('metadata_files', file_xlsx.name)

        risk_app = self.cleaned_data['riskapp']
        region = self.cleaned_data['region']
        risk = self.cleaned_data['riskanalysis']

        try:
            import_risk_metadata(tmp_file, risk_app.name, risk.name, region.name, final_name)
        except ValueError, e:
            raise forms.ValidationError(e)

        return file_xlsx

class ImportDataEventForm(models.ModelForm):
    """
    """

    class Meta:
        """
        """
        model = EventImportData
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
        model = EventImportAttributes
        fields = ('riskapp', 'region', 'riskanalysis', "adm_level_precision", "data_file",) #allow_null_values checkbox not shown

    def __init__(self, *args, **kwargs):
        super(ImportDataEventAttributeForm, self).__init__(*args, **kwargs)        
        if not self.current_user.is_superuser:
            self.fields['region'].queryset = Region.objects.filter(
                                            owner=self.current_user)
            self.fields['riskanalysis'].queryset = RiskAnalysis.objects.filter(
                                            owner=self.current_user)
    
    def clean_data_file(self):
        file_xlsx = self.cleaned_data['data_file']
        path = default_storage.save('tmp/'+file_xlsx.name,
                                    ContentFile(file_xlsx.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        final_name = os.path.join('data_files', file_xlsx.name)

        risk_app = self.cleaned_data['riskapp']
        region = self.cleaned_data['region']  
        risk = self.cleaned_data['riskanalysis']
        allow_null_values = False#self.cleaned_data['allow_null_values']
        adm_level_precision = self.cleaned_data['adm_level_precision']
        current_user = self.current_user
                
        import_event_attributes.delay(tmp_file, risk_app.name, risk.name, region.name, allow_null_values, final_name, current_user.id, adm_level_precision)        

        return file_xlsx
