from django.dispatch import Signal, receiver
from geonode.notifications_helper import send_now_notification
#from django.core.mail import send_mail
from geonode.people.models import Profile


data_uploaded = Signal(providing_args=['user', 'filename', 'region'])

def complete_upload(user, filename, region):    
    data_uploaded.send(sender=user.__class__, user=user, filename=filename, region=region)

@receiver(data_uploaded)
def notify_user_data_uploaded(sender, **kwargs):
    if kwargs['filename']:
        filename = kwargs['filename']
    if kwargs['user']:
        user = Profile.objects.get(id=kwargs['user'])    
    region = kwargs['region'] if kwargs['region'] else ''

    if filename and user:
        send_now_notification(
            users=[user],
            label="data_uploaded",
            extra_context={"from_user": user, "filename": filename, "region": region}
        )

        '''send_mail(
            'Data Uploaded',
            'Finished uploading file {}'.format(filename),
            'EC-DRMKC-NOREPLY@ec.europa.eu',
            [user.email],
            fail_silently=False
        )'''

