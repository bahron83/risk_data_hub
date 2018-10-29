from django.dispatch import Signal, receiver
#from django.db.models.signals import m2m_changed, post_save
from risks.models import RiskAnalysis, RiskAnalysisDymensionInfoAssociation
from geonode.notifications_helper import send_now_notification
from geonode.people.models import Profile
#from django.core.management import call_command
#import inspect


#SIGNALS RELATED TO ASYNCHRONOUS TASKS
data_uploaded = Signal(providing_args=['user', 'filename', 'region', 'additional_content'])
data_processing_failed = Signal(providing_args=['user', 'filename', 'region', 'error_message'])

def complete_upload(user, filename, region, additional_content=None):    
    data_uploaded.send(sender=user.__class__, user=user, filename=filename, region=region, additional_content=additional_content)

def report_processing_error(user, filename, region, error_message):
    data_processing_failed.send(sender=user.__class__, user=user, filename=filename, region=region, error_message=error_message)

@receiver(data_uploaded)
def notify_user_data_uploaded(sender, **kwargs):
    if kwargs['filename']:
        filename = kwargs['filename']
    if kwargs['user']:
        user = Profile.objects.get(id=kwargs['user'])    
    region = kwargs['region'] if kwargs['region'] else ''
    additional_content = kwargs['additional_content'] if kwargs['additional_content'] else ''

    if filename and user:
        send_now_notification(
            users=[user],
            label="data_uploaded",
            extra_context={"from_user": user, "filename": filename, "region": region, "additional_content": additional_content}
        )

@receiver(data_processing_failed)
def notify_user_data_processing_failed(sender, **kwargs):
    if kwargs['filename']:
        filename = kwargs['filename']
    if kwargs['user']:
        user = Profile.objects.get(id=kwargs['user'])    
    region = kwargs['region'] if kwargs['region'] else ''
    error_message = kwargs['error_message'] if kwargs['error_message'] else ''

    if filename and user:
        send_now_notification(
            users=[user],
            label="data_processing_failed",
            extra_context={"from_user": user, "filename": filename, "region": region, "error_message": error_message}
        )


#MODEL HOOKS
'''@receiver(m2m_changed)
def fix_relations_in_secondary_db(sender, **kwargs):        
    if kwargs['instance'] and kwargs['action']:            
        if kwargs['action'] == 'post_clear':
            if isinstance(kwargs['instance'], RiskAnalysis):
                risk_analysis = kwargs['instance']
                call_command('fix_diminfo_relations', risk_analysis_id=risk_analysis.id)'''

'''@receiver(post_save)  
def fix_relations_in_secondary_db(sender, **kwargs):        
    if kwargs['instance'] and not kwargs['created']:                    
            if sender == RiskAnalysis:
                risk_analysis = kwargs['instance']
                call_command('fix_diminfo_relations', risk_analysis_id=risk_analysis.id)'''