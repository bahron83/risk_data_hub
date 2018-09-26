from django.conf import settings
from django import forms
from django.db.models import Q
from django.views.generic import FormView
from django.http import HttpResponse, FileResponse
from geonode.layers.models import Layer
from risks.models import (RiskApp, FurtherResource, HazardType, AnalysisType, 
                            RiskAnalysis, DymensionInfo, Region, AdministrativeDivision,
                            RiskAnalysisDymensionInfoAssociation)
from risks.datasource import GeoserverDataSource


class AppAware(object):
    DEFAULT_APP = RiskApp.APP_DATA_EXTRACTION

    def get_app_name(self):
        return self.kwargs['app']

    def get_app(self):
        app_name = self.get_app_name()
        return RiskApp.objects.get(name=app_name)


class ContextAware(AppAware):

    CONTEXT_KEYS = ['ht', 'at', 'an', 'dym']

    def get_context_url(self, **kwargs):
        out = []
        if kwargs.pop('_full', None):
            ctx_keys = ['app', 'loc' ] + self.CONTEXT_KEYS
        else:
            ctx_keys = self.CONTEXT_KEYS
        for k in ctx_keys:
            if kwargs.get(k):
                out.extend([k, kwargs[k]])
            else:
                break
        if out:
            url = '{}/'.format('/'.join(out))
        else:
            url = None
        return url

    def fr_for_an(self, an, **kwargs):
        """
        .. py:method: ft_for_an(an, **kwargs)

        :param an: Risk Analysis object
        :param dict kwargs: other parameters available
        :type an: :py:class: rdh.risks.models.RiskAnalysis

        Returns list of :py:class: rdh.risks.models.FurtherResource
            related to Hazard type (assigned to Risk Analysis). Region may be used to narrow results.

        """
        if an.hazardset is None:
            return []
        region = None
        #if kwargs.get('loc'):
            #region = kwargs['loc'].region
        if kwargs.get('reg'):
            region = kwargs['reg']

        return FurtherResource.for_hazard_set(an.hazardset, region=region)


    def fr_for_dym(self, dym, **kwargs):
        """
        .. py:method: fr_for_dym(dym, **kwargs)

        :param dym: DymensionInfo object
        :param dict kwargs: other parameters for query
        :type dym: :py:class: rdh.risks.models.DymensionInfo

        Returns list of :py:class: rdh.risks.models.FurtherResource
            related to DymensionInfo. Region and Risk Analysis may be used to
            narrow results.
        """


        if dym is None:
            return []
        ranalysis = kwargs.get('an')
        region = None
        #if kwargs.get('loc'):
            #region = kwargs['loc'].region
        if kwargs.get('reg'):
            region = kwargs['reg']
        return FurtherResource.for_dymension_info(dym, region=region, ranalysis=ranalysis)


    def fr_for_at(self, at, **kwargs):
        """
        .. py:method: fr_for_at(dym, **kwargs)

        :param at: AnalysisType object
        :param dict kwargs: other parameters for query
        :type dym: :py:class: rdh.risks.models.DymensionInfo

        Returns list of :py:class: rdh.risks.models.FurtherResource
            related to DymensionInfo. Region and Risk Analysis may be used to
            narrow results.
        """
        if at is None:
            return []
        htype = kwargs.get('ht')
        region = None
        #if kwargs.get('loc'):
            #region = kwargs['loc'].region
        if kwargs.get('reg'):
            region = kwargs['reg']
        return FurtherResource.for_analysis_type(at, region=region, htype=htype)


    # maps url captured argument to specific class and field for lookup
    CONTEXT_KEYS_CLASSES = (('ht', HazardType, 'mnemonic'),
                            ('at', AnalysisType, 'name',),
                            ('an', RiskAnalysis, 'id',),
                            ('dym', DymensionInfo, 'id',),
                            ('reg', Region, 'name',),
                            ('loc', AdministrativeDivision, 'code',)
                            )


    def get_further_resources_inputs(self, **kwargs):
        """
        .. py:method:: get_further_resources_inputs(self, **kwargs)

        :param dict kwargs: keyword arguments obtained from url parser
        :return: dictionary with objects for keyword and criteria

        This will check each pair of (key, value) from url kwargs and,
        using map between key and class, will get specific object identified
        by value.

        """

        out = {}
        for k, klass, field in self.CONTEXT_KEYS_CLASSES:
            if not kwargs.get(k):
                continue
            related = self._get_from_kwargs(klass, field, kwargs[k])
            out[k] = related
        return out

    def get_further_resources(self, **kwargs):
        """
        .. py:method:: get_further_resources(self, **kwargs)

        returns map of criteria and further resources available for given criteria

        :param dict kwargs: keyword arguments obtained from url parser (see CONTEXT_KEY_CLASSES)
        :return: dictionary with object type name and list of related resources
        :rtype: dict

        """
        inputs = kwargs.pop('inputs', None) or self.get_further_resources_inputs(**kwargs)
        out = {}
        for res_type, key_name in (('at', 'analysisType',),
                                    ('dym', 'hazardSet',),
                                    ('an', 'hazardType',)):
            res_type_handler = getattr(self, 'fr_for_{}'.format(res_type))
            if kwargs.get(res_type):
                res_list = res_type_handler(**inputs)
                out[key_name] = self._fr_serialize(res_list)
        return out


    def _fr_serialize(self, items):
        return [i.export() for i in items]

    def _get_from_kwargs(self, klass, field, field_val):
        app = self.get_app()
        kwargs = {field: field_val}
        if hasattr(klass, 'app'):
            kwargs['app'] = app
        return klass.objects.get(**kwargs)


class FeaturesSource(object):

    AXIS_X = 'x'
    AXIS_Y = 'y'
    KWARGS_MAPPING = {'loc': 'adm_code',
                      'ht': 'hazard_type',
                      'an': 'risk_analysis',
                      'evt': 'event_id'}

    def url_kwargs_to_query_params(self, **kwargs):
        out = {}
        for k, v in kwargs.iteritems():
            if self.KWARGS_MAPPING.get(k):
                new_k = self.KWARGS_MAPPING[k]
                out[new_k] = v
        return out

    def get_dim_association(self, analysis, dyminfo):
        ass_list = RiskAnalysisDymensionInfoAssociation.objects.filter(riskanalysis=analysis, dymensioninfo=dyminfo)
        dim_list = set([a.axis_to_dim() for a in ass_list])
        if len(dim_list) != 1:
            raise ValueError("Cannot query more than one dimension at the moment, got {}".format(len(dim_list)))

        return (ass_list.first(), list(dim_list)[0])

    def get_dymlist_field_mapping(self, analysis, dimension, dymlist):
        out = []
        layers = [analysis.layer.typename]
        current_dim_name = self.get_dim_association(analysis, dimension)[1]
        out.append(current_dim_name)
        for dym in dymlist:
            if dym != dimension:
                dim_association = self.get_dim_association(analysis, dym)
                out.append(dim_association[1])
        return (out, layers)

    def get_features(self, analysis, dimension, dymlist, **kwargs):

        (dymlist_to_fields, dym_layers) = self.get_dymlist_field_mapping(analysis, dimension, dymlist)

        s = settings.OGC_SERVER['default']
        gs = GeoserverDataSource('{}/wfs'.format(s['LOCATION'].strip("/")),
                                 username=s['USER'],
                                 password=s['PASSWORD']
                                 )        
        dim_name = dymlist_to_fields[0]        
        layer_name = dym_layers[0]        
        #if 'additional_data' in kwargs:
        #    layer_name = '{}_{}'.format(layer_name, kwargs['additional_data'])
        #features = gs.get_features(layer_name, dim_name, **kwargs)
        features = gs.get_features(layer_name, None, **kwargs)
        return features

    def get_features_base(self, layerName, field_list, **kwargs):
        s = settings.OGC_SERVER['default']
        gs = GeoserverDataSource('{}/wfs'.format(s['LOCATION'].strip("/")),
                                 username=s['USER'],
                                 password=s['PASSWORD']
                                 )
        features = gs.get_features(layerName, field_list, **kwargs)
        return features


class LocationSource(object):

    def get_region(self, **kwargs):
        try:
            return Region.objects.get(name=kwargs['reg'])            
        except Region.DoesNotExist:
            return

    def get_location_exact(self, loc):
        try:
            return AdministrativeDivision.objects.get(code=loc)            
        except AdministrativeDivision.DoesNotExist:
            return
    
    def get_location(self, **kwargs):
        loc = self.get_location_exact(kwargs['loc'])
        try:
            locations = loc.get_parents_chain() + [loc]
            return locations
        except:
            pass

    def get_location_range(self, loc):
        return AdministrativeDivision.objects.filter(code__in=loc)        
    
    def location_lookup(self, **kwargs):
        #matches = AdministrativeDivision.objects.filter(name__icontains=kwargs['admlookup'])
        qstring = kwargs['admlookup']
        matches = AdministrativeDivision.objects.filter(
            Q(name=qstring) | Q(name__icontains=qstring)
        ).extra(
            select={'match': 'name = %s'},
            select_params=(qstring,)
        ).order_by('-match', 'name')
        loc_chains = []
        if matches:            
            for loc in matches[:10]:
                loc_chains.append(loc.get_parents_chain() + [loc])
        return loc_chains


class LayersListForm(forms.Form):
    layers = forms.MultipleChoiceField(required=False, choices=())

    def get_layers(self):
        if not self.is_valid():
            return []
        d = self.cleaned_data
        return Layer.objects.filter(id__in=d['layers'])


class RiskLayersView(FormView):
    form_class = LayersListForm

    def get_risk(self):
        rid = self.kwargs['risk_id']
        try:
            return RiskAnalysis.objects.get(id=rid)
        except RiskAnalysis.DoesNotExist:
            pass

    def get_layer_choices(self):
        r = self.get_risk()
        if r.layer is None:
            q = Layer.objects.all().values_list('id', flat=True)
        else:
            q = Layer.objects.exclude(id=r.layer.id).values_list('id', flat=True)
        return [(str(val), str(val),) for val in q]

    def get_form(self, form_class=None):
        f = super(RiskLayersView, self).get_form(form_class)
        choices = self.get_layer_choices()
        f.fields['layers'].choices = choices
        return f


    def form_invalid(self, form):
        err = form.errors
        return json_response({'errors': err}, status=400)

    def form_valid(self, form):
        rid = self.kwargs['risk_id']
        risk = self.get_risk()
        if risk is None:
            return json_response({'errors': ['Invalid risk id']}, status=404)

        data = form.cleaned_data

        risk.additional_layers.clear()
        layers = form.get_layers()
        risk.additional_layers.add(*layers)
        risk.save()
        return self.get()


    def get(self, *args, **kwargs):
        rid = self.kwargs['risk_id']
        risk = self.get_risk()
        if risk is None:
            return json_response({'errors': ['Invalid risk id']}, status=404)
        out = {}
        out['success'] = True
        out['data'] = {'layers': list(risk.additional_layers.all().values_list('typename', flat=True))}
        return json_response(out)


class CleaningFileResponse(FileResponse):
    def __init__(self, *args, **kwargs):

        on_close = kwargs.pop('on_close', None)
        super(CleaningFileResponse, self).__init__(*args, **kwargs)
        self._on_close = on_close

    def close(self):
        print('closing', self)
        if callable(self._on_close):
            self._on_close()
        super(CleaningFileResponse, self).close()