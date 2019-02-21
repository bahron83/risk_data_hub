#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import StringIO
from celery import shared_task
from django.conf import settings
from django.core.management import call_command
from django.db import IntegrityError, transaction
from risks.models import Region, DamageAssessment, HazardSet, Hazard
from risks.signals import complete_upload, report_processing_error


@shared_task
def create_damage_assessment(input_file, final_name, current_user_id):
    out = StringIO.StringIO()
    da = None
    try:
        call_command('create_da',
                     descriptor_file=str(input_file).strip(), current_user=current_user_id, stdout=out)
        value = out.getvalue()

        da = DamageAssessment.objects.get(name=str(value).strip())
        print('risk found: {}'.format(da.name))
        '''try:
            with transaction.atomic():
                risk.descriptor_file = file_ini
                risk.save()            
        except IntegrityError:            
	        pass'''
        da.descriptor_file = final_name
        da.save()

    except Exception, e:
        value = None
        if da is not None:
            da.set_error()
        error_message = "Sorry, the input file is not valid: {}".format(e)
        raise ValueError(error_message)

@shared_task
def import_risk_data(filepath, risk_app_name, damage_assessment_name, region_name, final_name, current_user_id):
        try:
            da = DamageAssessment.objects.get(name=damage_assessment_name)
        except DamageAssessment.DoesNotExist:
            raise ValueError("Damage Assessment not found")
        da.set_queued()
        out = StringIO.StringIO()         
        try:            
            da.set_processing()            
            call_command('importriskdata',
                         commit=False,
                         risk_app=risk_app_name,
                         region=region_name,
                         excel_file=filepath,
                         damage_assessment=damage_assessment_name,   
                         stdout=out)            
        except Exception, e:            
            #da.save()
            da.set_error()
            report_processing_error(current_user_id, final_name, region_name, e)    
            return None

        da.refresh_from_db()
        da.data_file = final_name
        da.save()
        da.set_ready()
        complete_upload(current_user_id, final_name, region_name)

@shared_task
def import_risk_metadata(filepath, risk_app_name, damage_assessment_name, region_name, final_name):        
        try:
            da = DamageAssessment.objects.get(name=damage_assessment_name)
        except DamageAssessment.DoesNotExist:
            raise ValueError("Damage Assessment not found")
        da.set_queued()
        out = StringIO.StringIO()
        try:            
            da.set_processing()
            call_command('import_risk_metadata',
                         commit=False,
                         risk_app=risk_app_name,
                         region=region_name,
                         excel_file=filepath,
                         damage_assessment=damage_assessment_name,
                         stdout=out)            
            da.refresh_from_db()
            da.metadata_file = final_name
            hazardsets = HazardSet.objects.filter(damage_assessment__name=damage_assessment_name,
                                                  country__name=region_name)
            if len(hazardsets) > 0:
                hazardset = hazardsets[0]
                da.hazardset = hazardset

            da.save()
            da.set_ready()
        except Exception, e:
            error_message = "Sorry, the input file is not valid: {}".format(e)
            if da is not None:
                da.set_error()
            raise ValueError(error_message)

@shared_task
def import_event_data(filepath, risk_app_name, damage_assessment_name, region_name, filename_ori, current_user_id):
        try:
            da = DamageAssessment.objects.get(name=damage_assessment_name)
        except DamageAssessment.DoesNotExist:
            raise ValueError("Damage Assessment not found")
        try:
            region = Region.objects.get(name=region_name)
        except Region.DoesNotExist:
            raise ValueError("Region not found")
        da.set_queued()      
        out = StringIO.StringIO()        
        event_codes = None       
        try:            
            call_command('importeventdata',                         
                         risk_app=risk_app_name,
                         region=region_name,
                         excel_file=filepath,                         
                         damage_assessment=damage_assessment_name,
                         stdout=out)  
            event_codes = out.getvalue()                       
        except Exception, e:
            da.save()
            da.set_error()        
            report_processing_error(current_user_id, filename_ori, region_name, e)    
            return None
        
        da.refresh_from_db()        
        da.data_file = filename_ori
        da.save()
        da.set_ready()            
        complete_upload(current_user_id, filename_ori, region_name, event_codes)           

@shared_task
def import_event_attributes(filepath, risk_app_name, damage_assessment_name, region_name, allow_null_values, final_name, current_user_id, adm_level_precision):        
        try:
            da = DamageAssessment.objects.get(name=damage_assessment_name)
        except DamageAssessment.DoesNotExist:
            raise ValueError("Damage Assessment not found")
        try:
            region = Region.objects.get(name=region_name)
        except Region.DoesNotExist:
            raise ValueError("Region not found")
        da.set_queued()      
        out = StringIO.StringIO()          
        try:  
            da.set_processing()          
            call_command('import_event_attributes',
                         commit=False,
                         risk_app=risk_app_name,                         
                         region=region_name,
                         allow_null_values=allow_null_values,
                         excel_file=filepath,
                         damage_assessment=damage_assessment_name,
                         adm_level_precision=adm_level_precision, 
                         stdout=out)            
        except Exception, e:    
            da.save()
            da.set_error()        
            report_processing_error(current_user_id, final_name, region_name, e)    
            return None

        da.refresh_from_db()
        da.region=region
        da.data_file = final_name
        da.save()
        da.set_ready()            
        complete_upload(current_user_id, final_name, region_name)             

        
