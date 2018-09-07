import json
from risk_data_hub import settings as rdh_settings
from geonode.utils import json_response
from django.views.generic import View
from risks.views.base import ContextAware
from risks.models import Region


UNRESTRICTED_REGIONS = ['Europe', 'EUWaters', 'South_Eastern_Europe']

class UserAuth(object):
    
    def is_user_allowed(self, request, **kwargs):
        if request.user.is_superuser:
            return True
        
        owner_groups = None    
        if request.method == 'POST':        
            data = json.loads(request.body)             
            if data['requestContext'] == 'region':
                if 'app' in data:            
                    region_name = data['app']['regionName']
                    try:
                        region = Region.objects.get(name=region_name)                        
                    except Region.DoesNotExist:
                        pass
                    if region.name in UNRESTRICTED_REGIONS:
                        return True
                    if region.owner:
                        owner_groups = region.owner.groups.all()                        
        elif request.method == 'GET':        
            if kwargs['requestContext'] == 'risk_analysis':
                if 'risk_analysis' in kwargs:
                    risk_analysis = kwargs['risk_analysis']
                    if risk_analysis.region:
                        if risk_analysis.region.name in UNRESTRICTED_REGIONS:
                            return True
                    if risk_analysis.owner:
                        owner_groups = risk_analysis.owner.groups.all()        
        if owner_groups:
            current_user = request.user
            current_user_group_ids = current_user.groups.all().values_list('id', flat=True)            
            if owner_groups.filter(pk__in=current_user_group_ids).exists():
                return True
            # else:
               # if not owner_groups.filter(name=rdh_settings.COUNTRY_ADMIN_USER_GROUP).exists():                
                   # return True
        
        return False

    def prepare_response(self, status, code, message = ''):
        return {
            'status': status,
            'code': code,
            'message': message
        }
    
    def validate_request(self, request, **kwargs):   
        data = json.loads(request.body)     
        if not 'requestContext' in data:
            return self.prepare_response('error', 400, 'No context specified in the request')
        if not 'app' in data:
            return self.prepare_response('error', 400, 'No app specified in the request')
        elif data['requestContext'] == 'region':
            if 'app' in kwargs:                            
                try:
                    region_name = data['app']['regionName']
                    region = Region.objects.get(name=region_name)                    
                except KeyError, e:
                    return self.prepare_response('error', 400, e)
                except Region.DoesNotExist:    
                    return self.prepare_response('error', 404, 'No data available for selected country')
        return self.prepare_response('ok', 200)


class AuthorizationView(ContextAware, View):    
    
    def post(self, request, *args, **kwargs):   
        user_auth = UserAuth()     
        request_validation = user_auth.validate_request(request, **kwargs)
        if request_validation['status'] == 'ok':
            if not user_auth.is_user_allowed(request, **kwargs):
                return json_response(errors=['You are not allowed to access the requested resources'], status=403)                
        else:
            return json_response(errors=[request_validation['message']], status=request_validation['code'])
        
        return json_response({'success': True})
                