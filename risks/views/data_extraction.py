import os
import datetime
from decimal import *
from itertools import groupby
from dateutil.parser import parse
from django.conf import settings
from django.db.models import FloatField
from django.db.models.functions import Cast
from risk_data_hub import settings as rdh_settings
from geonode.utils import json_response
from risks.views.base import FeaturesSource, LocationSource
from risks.views.hazard_type import HazardTypeView
from risks.views.auth import UserAuth
from risks.models import DamageAssessment, DamageType, AnalysisType, Event, AdministrativeData
from risks.overrides.postgres_jsonb import KeyTextTransform, KeyTransform


EVENTS_TO_LOAD = 50
SENDAI_FROM_YEAR = 2005
SENDAI_TO_YEAR = 2015
SENDAI_YEARS_TIME_SPAN = 10
DEFAULT_DECIMAL_POINTS = 5

class DataExtractionView(FeaturesSource, HazardTypeView):             

    def calculate_sendai_indicator(self, loc, indicator, events_total, output_type = 'sum', n_of_years = 1):
        result = None 
        multiplier = 1          
        adm_data_value = None
        baseline_unit = ''
        if indicator:             
            if indicator.name.startswith('A') or indicator.name.startswith('B'):
                try:
                    adm_data = AdministrativeData.objects.get(name='Population')
                except AdministrativeData.DoesNotExist:
                    pass
                multiplier = 100000           
            elif indicator.name.startswith('C'):
                try:
                    adm_data = AdministrativeData.objects.get(name='GDP')                 
                except AdministrativeData.DoesNotExist:
                    pass
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

    def format_risk_analysis_values(self, features, locations=[], include_loc=False):
        values = []                
        loc_codes = [l.code for l in locations] if locations else []
        for f in features: 
            entry = f.entry
            check = True
            if locations and entry['administrative_division']['code'] not in loc_codes:
                check = False
            if check:                
                row_value = [entry['dim1']['value'], entry['dim2']['value'], entry['value']]
                if include_loc and locations:
                    row_value.insert(0, entry['administrative_division']['code'])
                values.append(row_value)        
        return values

    def format_data_dimensions(self, risk, dimension, dimensions):
        dims = [dimension.set_risk_analysis(risk)] + [d.set_risk_analysis(risk) for d in dimensions if d.id != dimension.id]
        return [dim.set_risk_analysis(risk).export() for dim in dims]

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
        (atype_r, atype_e, atypes, scope,) = self.get_analysis_type(reg, loc, hazard_type, **kwargs)        
        current_atype = None
        risk = None
        if not atype_r:
            if atype_e:
                if atype_e.scope == scope:
                    current_atype = atype_e
        else:
            if atype_r.scope == scope:
                current_atype = atype_r
            if atype_e: 
                if atype_e.scope == scope:
                    current_atype = atype_e        
        if not current_atype:
            return json_response(errors=['No analysis type available for location/hazard type'], status=404) 
        
        # Check risk analysis
        try:
            risk = DamageAssessment.objects.get(pk=kwargs['an'])
        except DamageAssessment.DoesNotExist:
            return json_response(errors=['No risk analysis found for given parameters'], status=404)        

        # Check user permissions
        user_auth = UserAuth()
        available_datasets, dataset_rule_association = user_auth.resolve_available_datasets(request, reg)        
        if risk not in available_datasets:
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
            'scope': risk.analysis_type.scope,
            'full_url': context_url + '/risks/' + app.name + '/reg/' + reg.name + '/loc/' + loc.code + '/ht/' + hazard_type.mnemonic + '/at/' + current_atype.name + '/an/' + str(risk.id) + '/'
        }
        
        # Resolve main dimension/axis        
        dymlist = risk.damage_types.all().distinct()
        if kwargs.get('dym'):
            dimension = dymlist.get(id=kwargs['dym'])
        else:
            dimension = dymlist.filter(damageassessment_association__axis=self.AXIS_X).distinct().get()        

        # Apply visibility rules
        values_after_visibility_rules = user_auth.filter_dataset_values(risk, dataset_rule_association)

        # Start building output
        out = {'riskAnalysisData': risk.get_risk_details()}
        #out['riskAnalysisData']['data'] = self.format_risk_analysis_features(risk, dimension, dymlist, features)        
        out['riskAnalysisData']['style'] = risk.style.custom_export() if risk.style else None
        out['riskAnalysisData']['data'] = {}
        out['riskAnalysisData']['data']['dimensions'] = self.format_data_dimensions(risk, dimension, dymlist)
        
        out['context'] = self.get_context_url(**kwargs)        
        out['riskAnalysisData']['unitOfMeasure'] = risk.unit_of_measure
        out['riskAnalysisData']['additionalLayers'] = [(l.id, l.typename, l.title, ) for l in risk.additional_layers.all()]
        out['furtherResources'] = self.get_further_resources(**kwargs)
        #url(r'loc/(?P<loc>[\w\-]+)/ht/(?P<ht>[\w\-]+)/at/(?P<at>[\w\-]+)/an/(?P<an>[\w\-]+)/pdf/$', views.pdf_report, name='pdf_report'),
        out['pdfReport'] = app.url_for('pdf_report', loc.code, hazard_type.mnemonic, current_atype.name, risk.id)
        out['fullContext'] = full_context
        
        # RISK ANALYSIS
        if risk.analysis_type.scope == 'risk':        
            # Retrieve values of current location (for charts) and children locations (for map)
            locations_needed = [loc] + list(loc.get_children()) if loc.has_children() else [loc]        
            loc_codes = [l.code for l in locations_needed]
            values = values_after_visibility_rules \
                .filter(entry__administrative_division__code__in=loc_codes) \
                .annotate(
                    adm_code=KeyTextTransform('code', KeyTransform('administrative_division', 'entry')),
                    dim1_value=KeyTextTransform('value', KeyTransform('dim1', 'entry')),
                    dim2_value=Cast(KeyTextTransform('value', KeyTransform('dim2', 'entry')), FloatField())
                ) \
                .order_by('adm_code', 'dim1_value', 'dim2_value')
            loc_values = self.format_risk_analysis_values(values, [loc])
            children_values = self.format_risk_analysis_values(values, list(loc.get_children()), True)
        
            out['riskAnalysisData']['data']['values'] = loc_values
            out['riskAnalysisData']['data']['subunits_values'] = children_values

        # HISTORICAL EVENTS
        elif risk.analysis_type.scope == 'event':                                    

            # Retrieve events from Django
            events = Event.objects.filter(hazard_type=hazard_type, region=reg, state='ready')
            if loc.level > 0:
                events = events.filter(country__in=[loc]+loc.get_parents_chain())            
            
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

            # Retrieve Damage Assessment Entries for Events
            event_entries = values_after_visibility_rules \
                .filter(entry__has_key='phenomenon', entry__administrative_division__level__gte=loc.level)
            
            # Retrieve values for events aggregated by country
            # Since Django doesn't allow yet Subquery expression with aggregation, sum operations are computed in memory
            # The equivalent SQL query would be
            # SELECT country, SUM(val) AS totals FROM (
            #    SELECT entry->'event'->>'country' as country, (entry->>'value')::float AS val
            #    FROM risks_damage_assessment_entry
            #    WHERE entry->'event'->>'country' IS NOT null
            #    AND entry->>'region' = '%region%'
            #    AND entry->>'damage_assessment' = '%damage_assessment%'
            #    GROUP BY country, val
            # ) t1
            # GROUP BY country                        
            
            event_entries_by_country = event_entries \
                .annotate(
                    country=KeyTextTransform('country', KeyTransform('event', 'entry')),
                    value=Cast(KeyTextTransform('value', 'entry'), FloatField())
                ) \
                .order_by('country') \
                .values('country', 'value')

            event_values_group_country = {}            
            for k,v in groupby(event_entries_by_country,key=lambda x:x['country']):
                event_values_group_country[k] = sum(f['value'] for f in v)                                            

            # Build final event list (~ [Events] LEFT JOIN [DamageAssessmentEntry])
            ev_list = []
            data_key = None
            for event in events:
                e = event.custom_export()  
                if event_entries.exists():
                    phenomenon_ids = [p['id'] for p in e['phenomena']]                    
                    e[data_key] = None                
                    try:              
                        event_entry = event_entries.filter(entry__phenomenon__id__in=phenomenon_ids)
                        data_key = event_entry[0].entry['dim1']['value']
                        e[data_key] = round(Decimal(event_entry[0].entry['value']), DEFAULT_DECIMAL_POINTS)
                        index_of_p = 0
                        for p in e['phenomena']:                            
                            e['phenomena'][index_of_p]['value'] = event_entry.get(entry__phenomenon__id=p['id']).entry['phenomenon']['value']
                            index_of_p += 1
                    except:                    
                        pass
                    e['data_key'] = data_key                
                ev_list.append(e)

            # Sendai indicator
            sendai_final_array = []   
            diminfo = dimension.set_risk_analysis(risk).get_axis().first()                     
            if diminfo.sendai_indicator:                     
                
                # Getting values needs an additional in memory process, since Django ORM does not allow complex subqueries
                # Equivalent SQL is
                # SELECT country, ev_year, sum(val) AS totals FROM (
                # 	SELECT entry->'event'->>'country' as country, entry->'event'->>'year' as ev_year, (entry->>'value')::float AS val
                # 	FROM risks_damage_assessment_entry
                # 	WHERE entry->'event'->>'country' IS NOT null
                # 	AND entry->>'region' = 'Europe'
                # 	--AND entry->>'damage_assessment' = ''
                # 	GROUP BY country, ev_year, val
                # 	ORDER BY country, ev_year
                # ) t1
                # GROUP BY country, ev_year
                features_sendai_temp = event_entries \
                    .filter(entry__event__country=loc.code, entry__event__year__gte=SENDAI_FROM_YEAR) \
                    .annotate(
                        country=KeyTextTransform('country', KeyTransform('event', 'entry')),
                        year=KeyTextTransform('year', KeyTransform('event', 'entry')),
                        value=Cast(KeyTextTransform('value', 'entry'), FloatField())
                    ) \
                    .order_by('country', 'year') \
                    .values('country', 'year', 'value')

                features_sendai = {}
                for k,v in groupby(features_sendai_temp,key=lambda x:x['year']):
                    features_sendai[k] = sum(f['value'] for f in v)                    
                    
                total = 0
                n_of_years = 0
                '''for year in range(SENDAI_TO_YEAR, datetime.datetime.now().year + 1):                    
                    from_year = year - SENDAI_YEARS_TIME_SPAN
                    for s in features_sendai:                        
                        if s[0] >= from_year and s[0] <= year:                             
                            total += s[1]                                                        
                    sendai_final_array.append(['{}_{}'.format(from_year, year), self.calculate_sendai_indicator(loc, sendai_indicator, total)])
                    total = 0'''
                                
                for key,value in features_sendai.iteritems():
                    if int(key) >= SENDAI_FROM_YEAR:
                        if int(key) <= SENDAI_TO_YEAR:                            
                            total += value
                            n_of_years += 1
                        #else: #removing else will display all years instead of grouping years from 2005 to 2015
                        rounded_value = round(Decimal(value), DEFAULT_DECIMAL_POINTS)
                        sendai_value, baseline_unit = self.calculate_sendai_indicator(loc, diminfo.sendai_indicator, rounded_value)
                        sendai_final_array.append([key, sendai_value, baseline_unit])
                sendai_average_value, baseline_unit = self.calculate_sendai_indicator(loc, diminfo.sendai_indicator, total, 'average', n_of_years)
                sendai_final_array.insert(0, ['{}_{}'.format(SENDAI_FROM_YEAR, SENDAI_TO_YEAR), sendai_average_value, baseline_unit])
                      
            # Finishing building output            
            out['riskAnalysisData']['eventAreaSelected'] = ''            
            out['riskAnalysisData']['data']['event_group_country'] = event_values_group_country
            out['riskAnalysisData']['data']['total_events'] = total_events         
            out['riskAnalysisData']['events'] = ev_list
            out['riskAnalysisData']['data']['sendaiValues'] = sendai_final_array
            out['riskAnalysisData']['decimalPoints'] = DEFAULT_DECIMAL_POINTS
        
        return json_response(out)    