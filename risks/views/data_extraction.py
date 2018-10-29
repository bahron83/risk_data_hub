import os
import datetime
from decimal import *
from dateutil.parser import parse
from django.conf import settings
from risk_data_hub import settings as rdh_settings
from geonode.utils import json_response
from risks.views.base import FeaturesSource, LocationSource
from risks.views.hazard_type import HazardTypeView
from risks.views.auth import UserAuth
from risks.models import RiskAnalysis, DymensionInfo, AnalysisType, Event, AdministrativeData


EVENTS_TO_LOAD = 50
SENDAI_FROM_YEAR = 2005
SENDAI_TO_YEAR = 2015
SENDAI_YEARS_TIME_SPAN = 10
DEFAULT_DECIMAL_POINTS = 5

class DataExtractionView(FeaturesSource, HazardTypeView):   

    def reformat_features(self, risk, dimension, dimensions, features, capitalize=False):
        """
        Returns risk data as proper structure

        """
        values = []
        dims = [dimension.set_risk_analysis(risk)] + [d.set_risk_analysis(risk) for d in dimensions if d.id != dimension.id]

        _fields = [self.get_dim_association(risk, d) for d in dims]
        fields = ['{}_value'.format(f[1]) for f in _fields]
        field_orders = ['{}_order'.format(f[1]) for f in _fields]

        orders = [dict(d.get_axis_order()) for d in dims]

        orders_len = len(orders)

        def make_order_val(feat):
            """
            compute order value
            """
            _order_vals = []

            for idx, o in enumerate(orders):
                field_name = field_orders[idx]
                val = feat['properties'].get(field_name)
                # order_val = o.get(val)
                order_val = val

                if order_val is None:
                    order_val = 0
                # 111 > 1, 1, 1
                # mag = 10 ** (orders_len - idx)
                mag = 1000 if idx == 0 else 1
                _order_vals.append(int('{}'.format(order_val * mag)))
            # return ''.join(_order_vals)
            return sum(_order_vals)

        def order_key(val):
            # order by last val
            order = val.pop(-1)
            return order

        for feat in features:
            p = feat['properties']
            line = []
            [line.append(p[f]) for f in fields]
            line.append(p['value'])
            line.append(make_order_val(feat))
            if capitalize:
                line = [str(item).capitalize() for item in line]
            values.append(line)

        values.sort(key=order_key)

        out = {'dimensions': [dim.set_risk_analysis(risk).export() for dim in dims],
               'values': values}

        return out  

    def features_to_list(self, features, field_list):
        features_list = []
        for f in features['features']:
            temp = []                
            for l in field_list:
                temp.append(f['properties'][l])
            features_list.append(temp)
        return features_list

    def features_to_object(self, features, field_list, key):
        features_obj = {}
        for f in features['features']:
            temp = []                
            for l in field_list:
                temp.append(f['properties'][l])            
            features_obj[temp[field_list.index(key)]] = temp
        return features_obj

    def get_features_list(self, layer_name, field_list, **kwargs):
        features = self.get_features_base(layer_name, field_list, **kwargs)
        return self.features_to_list(features, field_list)

    def get_features_obj(self, layer_name, field_list, object_key, **kwargs):
        features = self.get_features_base(layer_name, field_list, **kwargs)
        return self.features_to_object(features, field_list, object_key)

    def calculate_sendai_indicator(self, loc, indicator, events_total, output_type = 'sum', n_of_years = 1):
        result = None 
        multiplier = 1          
        adm_data_value = None
        baseline_unit = ''
        if indicator:             
            if indicator.code.startswith('A') or indicator.code.startswith('B'):
                adm_data = AdministrativeData.objects.get(name='Population')
                multiplier = 100000           
            elif indicator.code.startswith('C'):
                adm_data = AdministrativeData.objects.get(name='GDP')                 
                #adm_data_value = 1
                multiplier = 100
                baseline_unit = '%'
            if adm_data:
                adm_data_row = adm_data.set_location(loc).get_by_association()                
                if adm_data_row:
                    if not adm_data_value:
                        adm_data_value = float(adm_data_row.value)
                    result = events_total / adm_data_value * multiplier
                    if output_type == 'average' and n_of_years > 0:
                        result = round(Decimal(result / n_of_years), DEFAULT_DECIMAL_POINTS)
        return result, baseline_unit

    def get(self, request, *args, **kwargs):   
        
        # Check location
        reg = self.get_region(**kwargs)     
        locations = self.get_location(**kwargs)
        app = self.get_app()
        if not locations:
            return json_response(errors=['Invalid location code'], status=404)
        loc = locations[-1]

        # Check hazard type
        hazard_type = self.get_hazard_type(reg, loc, **kwargs)
        if not hazard_type:
            return json_response(errors=['Invalid hazard type'], status=404)

        # Check analysis type
        (atype_r, atype_e, atypes, aclass,) = self.get_analysis_type(reg, loc, hazard_type, **kwargs)        
        current_atype = None
        risks = None
        if not atype_r:
            if atype_e:
                if atype_e.analysis_class == aclass:
                    current_atype = atype_e
        else:
            if atype_r.analysis_class == aclass:
                current_atype = atype_r
            if atype_e: 
                if atype_e.analysis_class == aclass:
                    current_atype = atype_e        
        if not current_atype:
            return json_response(errors=['No analysis type available for location/hazard type'], status=404) 
        
        # Check risk analysis
        risks = current_atype.get_risk_analysis_list(id=kwargs['an'])
        if not risks:
            return json_response(errors=['No risk analysis found for given parameters'], status=404)
        risk = risks[0]

        # Check user permissions
        user_auth = UserAuth()
        user_auth_args = {
            'requestContext': 'risk_analysis',
            'risk_analysis': risk
        }
        if not user_auth.is_user_allowed(request, **user_auth_args):
            return json_response(errors=['Data not available for current user'], status=403)         
                
        # Context parameters
        parts = rdh_settings.SITEURL.replace('//', '').strip('/').split('/') if rdh_settings.SITEURL else []
        context_url = '/' + parts[len(parts)-1] if len(parts) > 1 else ''
        full_context = {
            'app': app.name,
            'reg': reg.name,
            'adm_level': loc.level,            
            'loc': loc.code,
            'ht': hazard_type.mnemonic,
            'at': current_atype.name,
            'an': risk.id,
            'analysis_class': risk.analysis_type.analysis_class.name,
            'full_url': context_url + '/risks/' + app.name + '/reg/' + reg.name + '/loc/' + loc.code + '/ht/' + hazard_type.mnemonic + '/at/' + current_atype.name + '/an/' + str(risk.id) + '/'
        }
        
        # Get risk analysis main features        
        dymlist = risk.dymension_infos.all().distinct()
        if kwargs.get('dym'):
            dimension = dymlist.get(id=kwargs['dym'])
        else:
            dimension = dymlist.filter(riskanalysis_associacion__axis=self.AXIS_X).distinct().get()

        feat_kwargs = self.url_kwargs_to_query_params(**kwargs)
        feat_kwargs['risk_analysis'] = risk.name        
        features = self.get_features(risk, dimension, dymlist, **feat_kwargs)
        
        # Start building output
        out = {'riskAnalysisData': risk.get_risk_details()}
        out['riskAnalysisData']['data'] = self.reformat_features(risk, dimension, dymlist, features['features'])        
        out['context'] = self.get_context_url(**kwargs)
        out['wms'] = {'style': None,
                      'viewparams': self.get_viewparams(risk, hazard_type, loc),
                      'baseurl': settings.OGC_SERVER['default']['PUBLIC_LOCATION']}
        out['riskAnalysisData']['unitOfMeasure'] = risk.unit_of_measure
        out['riskAnalysisData']['additionalLayers'] = [(l.id, l.typename, l.title, ) for l in risk.additional_layers.all()]
        out['furtherResources'] = self.get_further_resources(**kwargs)
        #url(r'loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/an/(?P<an>[\w\-]+)/pdf/$', views.pdf_report, name='pdf_report'),
        out['pdfReport'] = app.url_for('pdf_report', loc.code, hazard_type.mnemonic, current_atype.name, risk.id)
        out['fullContext'] = full_context

        # Handling of events
        if risk.analysis_type.analysis_class.name == 'event':                                    

            # Retrieve events from Django
            events = Event.objects.filter(hazard_type=hazard_type, region=reg)
            if loc.level == 1:
                events = events.filter(iso2=loc.code)
            elif loc.level >= 2:
                events = events.filter(nuts3__contains=loc.code)
            
            # Check if need to filter by date
            if events and 'from' in kwargs and 'to' in kwargs:
                try:
                    date_from = parse(kwargs.get('from'))
                    date_to = parse(kwargs.get('to'))
                    events = events.filter(begin_date__range=(date_from, date_to))
                except ValueError:
                    return json_response(errors=['Invalid date format'], status=400)
            
            events = events.order_by('-begin_date')  
            total_events = events.count()
            
            # Limit number of results
            if events and 'load' not in kwargs and 'from' not in kwargs:
                events = events[:EVENTS_TO_LOAD]
                #set limit also for Geoserver query
                feat_kwargs['limit'] = EVENTS_TO_LOAD            

            # Retrieve values for events aggregated by country from Geoserver
            field_list = ['adm_code', 'dim1_value', 'dim2_value', 'value', 'event_id']
            field_list_group = ['adm_code', 'dim1_value', 'dim2_value', 'value']
            feat_kwargs['level'] = loc.level                        
            event_group_country = self.get_features_list('geonode:risk_analysis_event_group', field_list_group, **feat_kwargs) if loc.level == 0 else None
            values_events = self.get_features_obj('geonode:risk_analysis_event_details', field_list, 'event_id', **feat_kwargs)
            
            # Build final event list (~ [Django] LEFT JOIN [Geoserver])
            ev_list = []
            data_key = values_events.values()[0][1]
            for event in events:
                e = event.get_event_plain()                
                e[data_key] = None                
                try:              
                    value_arr = values_events[e['event_id']]
                    e[data_key] = round(Decimal(value_arr[3]), DEFAULT_DECIMAL_POINTS)
                except:                    
                    pass
                e['data_key'] = data_key                
                ev_list.append(e)

            # Sendai indicator
            sendai_final_array = []
            field_list = ['year', 'value']
            feat_kwargs = {
                'risk_analysis': risk.name,
                'adm_code': loc.code,
                'from_year': SENDAI_FROM_YEAR
            }            
            diminfo = dimension.set_risk_analysis(risk).get_axis().first()
            if diminfo:
                sendai_indicator = diminfo.sendai_target
                if sendai_indicator: 
                    features_sendai = self.get_features_list('geonode:ra_event_values_grouped_by_year', field_list, **feat_kwargs)                                                       
                    total = 0
                    n_of_years = 0
                    '''for year in range(SENDAI_TO_YEAR, datetime.datetime.now().year + 1):                    
                        from_year = year - SENDAI_YEARS_TIME_SPAN
                        for s in features_sendai:                        
                            if s[0] >= from_year and s[0] <= year:                             
                                total += s[1]                                                        
                        sendai_final_array.append(['{}_{}'.format(from_year, year), self.calculate_sendai_indicator(loc, sendai_indicator, total)])
                        total = 0'''
                    for s in features_sendai:
                        if s[0] >= SENDAI_FROM_YEAR:
                            if s[0] <= SENDAI_TO_YEAR:                            
                                total += s[1]
                                n_of_years += 1
                            #else: #removing else will display all years instead of grouping years from 2005 to 2015
                            rounded_value = round(Decimal(s[1]), DEFAULT_DECIMAL_POINTS)
                            sendai_value, baseline_unit = self.calculate_sendai_indicator(loc, sendai_indicator, rounded_value)
                            sendai_final_array.append([s[0], sendai_value, baseline_unit])
                    sendai_average_value, baseline_unit = self.calculate_sendai_indicator(loc, sendai_indicator, total, 'average', n_of_years)
                    sendai_final_array.insert(0, ['{}_{}'.format(SENDAI_FROM_YEAR, SENDAI_TO_YEAR), sendai_average_value, baseline_unit])
                      
            # Finishing building output            
            out['riskAnalysisData']['eventAreaSelected'] = ''
            out['riskAnalysisData']['eventsLayer'] = {}
            out['riskAnalysisData']['eventsLayer']['layerName'] = '{}_events'.format(out['riskAnalysisData']['layer']['layerName'])
            out['riskAnalysisData']['eventsLayer']['layerStyle'] = {
                'name': 'monochromatic',
                'title': None,
                'url': 'http://localhost:8080/geoserver/rest/styles/monochromatic.sld'
            }
            #out['riskAnalysisData']['eventsLayer']['layerStyle']['url'] = out['riskAnalysisData']['layer']['layerStyle']['url']
            out['riskAnalysisData']['eventsLayer']['layerTitle'] = '{}_events'.format(out['riskAnalysisData']['layer']['layerTitle'])
            out['riskAnalysisData']['data']['event_group_country'] = event_group_country
            out['riskAnalysisData']['data']['total_events'] = total_events         
            out['riskAnalysisData']['events'] = ev_list
            out['riskAnalysisData']['data']['sendaiValues'] = sendai_final_array
            out['riskAnalysisData']['decimalPoints'] = DEFAULT_DECIMAL_POINTS
        
        return json_response(out)

    def get_viewparams(self, risk, htype, loc):
        return 'risk_analysis:{};hazard_type:{};adm_code:{};d1:{{}};d2:{{}}'.format(risk.name, htype.mnemonic, loc.code)