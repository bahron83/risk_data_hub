#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import StringIO
from celery import shared_task
from django.conf import settings
from django.core.management import call_command
from django.db import IntegrityError, transaction
from risks.models import Region, RiskAnalysis, HazardSet, HazardType
from risks.signals import complete_upload, report_processing_error


@shared_task
def create_risk_analysis(input_file, final_name, current_user_id):
    out = StringIO.StringIO()
    risk = None
    try:
        call_command('createriskanalysis',
                     descriptor_file=str(input_file).strip(), current_user=current_user_id, stdout=out)
        value = out.getvalue()

        risk = RiskAnalysis.objects.get(name=str(value).strip())
        print('risk found: {}'.format(risk.name))
        '''try:
            with transaction.atomic():
                risk.descriptor_file = file_ini
                risk.save()            
        except IntegrityError:            
	        pass'''
        risk.descriptor_file = final_name
        risk.save()

    except Exception, e:
        value = None
        if risk is not None:
            risk.set_error()
        error_message = "Sorry, the input file is not valid: {}".format(e)
        raise ValueError(error_message)

@shared_task
def import_risk_data(filepath, risk_app_name, risk_analysis_name, region_name, final_name, current_user_id):
        try:
            risk_analysis = RiskAnalysis.objects.get(name=risk_analysis_name)
        except RiskAnalysis.DoesNotExist:
            raise ValueError("Risk Analysis not found")
        risk_analysis.set_queued()
        out = StringIO.StringIO()         
        try:            
            risk_analysis.set_processing()            
            call_command('importriskdata',
                         commit=False,
                         risk_app=risk_app_name,
                         region=region_name,
                         excel_file=filepath,
                         risk_analysis=risk_analysis_name,   
                         stdout=out)            
        except Exception, e:            
            risk_analysis.save()
            risk_analysis.set_error()
            report_processing_error(current_user_id, final_name, region_name, e)    
            return None

        risk_analysis.refresh_from_db()
        risk_analysis.data_file = final_name
        risk_analysis.save()
        risk_analysis.set_ready()
        complete_upload(current_user_id, final_name, region_name)

@shared_task
def import_risk_metadata(filepath, risk_app_name, risk_analysis_name, region_name, final_name):        
        try:
            risk_analysis = RiskAnalysis.objects.get(name=risk_analysis_name)
        except RiskAnalysis.DoesNotExist:
            raise ValueError("Risk Analysis not found")
        risk_analysis.set_queued()
        out = StringIO.StringIO()
        try:            
            risk_analysis.set_processing()
            call_command('importriskmetadata',
                         commit=False,
                         risk_app=risk_app_name,
                         region=region_name,
                         excel_file=filepath,
                         risk_analysis=risk_analysis_name,
                         stdout=out)            
            risk_analysis.refresh_from_db()
            risk_analysis.metadata_file = final_name
            hazardsets = HazardSet.objects.filter(riskanalysis__name=risk_analysis_name,
                                                  country__name=region_name)
            if len(hazardsets) > 0:
                hazardset = hazardsets[0]
                risk_analysis.hazardset = hazardset

            risk_analysis.save()
            risk_analysis.set_ready()
        except Exception, e:
            error_message = "Sorry, the input file is not valid: {}".format(e)
            if risk_analysis is not None:
                risk_analysis.set_error()
            raise ValueError(error_message)

@shared_task
def import_event_data(filepath, risk_app_name, region_name, filename_ori, current_user_id):
        out = StringIO.StringIO()        
        event_ids = None       
        try:            
            call_command('importriskevents',
                         commit=False,
                         risk_app=risk_app_name,
                         region=region_name,
                         excel_file=filepath,                         
                         stdout=out)  
            event_ids = out.getvalue()                       
        except Exception, e:
            report_processing_error(current_user_id, filename_ori, region_name, e)    
            return None
        
        complete_upload(current_user_id, filename_ori, region_name, event_ids)           

@shared_task
def import_event_attributes(filepath, risk_app_name, risk_analysis_name, region_name, allow_null_values, final_name, current_user_id, adm_level_precision):        
        try:
            risk_analysis = RiskAnalysis.objects.get(name=risk_analysis_name)
        except RiskAnalysis.DoesNotExist:
            raise ValueError("Risk Analysis not found")
        try:
            region = Region.objects.get(name=region_name)
        except Region.DoesNotExist:
            raise ValueError("Region not found")
        risk_analysis.set_queued()      
        out = StringIO.StringIO()          
        try:  
            risk_analysis.set_processing()          
            call_command('import_event_attributes',
                         commit=False,
                         risk_app=risk_app_name,                         
                         region=region_name,
                         allow_null_values=allow_null_values,
                         excel_file=filepath,
                         risk_analysis=risk_analysis_name,
                         adm_level_precision=adm_level_precision, 
                         stdout=out)            
        except Exception, e:    
            risk_analysis.save()
            risk_analysis.set_error()        
            report_processing_error(current_user_id, final_name, region_name, e)    
            return None

        risk_analysis.refresh_from_db()
        risk_analysis.region=region
        risk_analysis.data_file = final_name
        risk_analysis.save()
        risk_analysis.set_ready()            
        complete_upload(current_user_id, final_name, region_name)             

        

