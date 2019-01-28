import sys
import json
from risk_data_hub import settings as rdh_settings
from geonode.utils import json_response
from django.views.generic import View
from risks.views.base import ContextAware
from risks.models import Region, AccessRule, AccessType, DamageAssessment, DamageAssessmentEntry
from risks.models.access_rule import get_generic_filter


UNRESTRICTED_REGIONS = ['Europe', 'EUWaters', 'South_Eastern_Europe']

class UserAuth(object):            
    def filter_damage_assessment(self, request, region, prev_data, rule, dataset_rule_association):                
        data = None
        res = prev_data
        skip = False        
        if rule.user:
            if rule.user != request.user:
                data = prev_data
                skip = True  
        if not skip:
            if rule.group:
                if not request.user.groups.all().filter(pk=rule.group.pk).exists():
                    data = prev_data
                    skip = True
        if not skip:
            # allow rule
            if rule.access == AccessType.ALLOW:            
                data = DamageAssessment.objects.filter(region=region)                            
                if rule.scope:
                    data = data.filter(analysis_type__scope=rule.scope)
                if rule.damage_assessment:
                    data = data.filter(pk=rule.damage_assessment.pk)                                                                            
                res = (data | prev_data).distinct() if prev_data else data.distinct()               
            # deny rule
            else:
                if prev_data:                                
                    if rule.scope:
                        data = prev_data.exclude(analysis_type__scope=rule.scope)
                    if rule.damage_assessment:
                        data = prev_data.exclude(pk=rule.damage_assessment.pk)                
                res = data
            # dataset rule association
            for d in data:
                if d.pk in dataset_rule_association:
                    dataset_rule_association[d.pk] += [rule]
                else:
                    dataset_rule_association[d.pk] = [rule]                            
        return res, dataset_rule_association 

    def filter_dataset_values(self, dataset, dataset_rule_association):        
        if dataset.id in dataset_rule_association:
            prev_data = None
            data = prev_data
            available_data = prev_data
            for rule in dataset_rule_association[dataset.id]:
                # allow rule
                if rule.access == AccessType.ALLOW:            
                    data = DamageAssessmentEntry.objects.filter(entry__damage_assessment=dataset.name)                                          
                    if rule.min_adm_level:
                        data = data.filter(entry__administrative_division__level__lte=rule.min_adm_level)
                    if rule.max_adm_level:
                        data = data.filter(entry__administrative_division__level__lte=rule.max_adm_level)                        
                    if rule.administrative_division_regex:
                        data = data.filter(entry__administrative_division__code__iregex=r'{}'.format(rule.administrative_division_regex))
                    available_data = (data | prev_data).distinct()  if prev_data else data.distinct()              
                # deny rule
                else:
                    if prev_data:                                
                        if rule.min_adm_level:
                            data = prev_data.exclude(entry__administrative_division__level__gte=rule.min_adm_level)
                        if rule.max_adm_level:
                            data = prev_data.exclude(entry__administrative_division__level__lte=rule.max_adm_level)
                        if rule.administrative_division_regex:
                            data = prev_data.exclude(entry__administrative_division__code__iregex=r'{}'.format(rule.administrative_division_regex))
                    available_data = data
                prev_data = available_data
            return available_data
        return None
    
    def is_dataset_available_for_user(self, dataset, request, region):
        avaiable_datasets, dataset_rule_association = self.resolve_available_datasets(request, region)
        return dataset in avaiable_datasets

    def get_dataset_values(self, dataset, request, region):
        avaiable_datasets, dataset_rule_association = self.resolve_available_datasets(request, region)
        if dataset in avaiable_datasets:
            return self.filter_dataset_values(dataset, dataset_rule_association)
        return None
    
    def resolve_available_datasets(self, request, region):   
        """
        Returns: 
        data -> all datasets that current user is allowed to access (DamageAssessment Queryset)
        dataset_rule_association -> ids of accessible datasets and relative rule(s) to be applied in given order to filter values
        """                     
        prev_data = None
        data = prev_data
        dataset_rule_association = {}
        check = False
        if request.user.is_superuser:
            check = True
        elif request.user.region:
            if request.user.region == region:
                check = True
        if check:
            rules = AccessRule.objects.filter(region=region).order_by('order')
            allow_filter = get_generic_filter()
            deny_filter = get_generic_filter()
            for rule in rules:            
                data, dataset_rule_association = self.filter_damage_assessment(request, region, prev_data, rule, dataset_rule_association)            
                prev_data = data
        available_datasets = data
        return available_datasets, dataset_rule_association                            
    
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
                