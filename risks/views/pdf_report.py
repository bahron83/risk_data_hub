import os
import json
from django import forms
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile, File
from django.views.generic import FormView
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from geonode.base.forms import ValuesListField
from risks.views.base import ContextAware
from risks.models import RiskAnalysis
from risks.pdf_helpers import generate_pdf


class PDFUploadsForm(forms.Form):
    map = forms.ImageField(required=True)
    chart_0 = forms.ImageField(required=True)
    chart_1 = forms.ImageField(required=False)
    chart_2 = forms.ImageField(required=False)
    chart_3 = forms.ImageField(required=False)
    legend = forms.ImageField(required=False)
    permalink = forms.URLField(required=False)
    dims = ValuesListField(required=True)
    dimsVal = ValuesListField(required=True)


class PDFReportView(ContextAware, FormView):
    form_class = PDFUploadsForm
    CONTEXT_KEYS = ContextAware.CONTEXT_KEYS + ['loc']
    TEMPLATE_NAME = 'risks/pdf/{}.{}.html'

    PDF_PARTS = ['cover', 'report', 'footer']

    def get_client_url(self, app, **kwargs):

        #http://localhost:8000/risks/data_extraction/?init={"href":"/risks/data_extraction/loc/AF/","geomHref":"/risks/data_extraction/geom/AF/","gc":"ht/EQ/","ac":"ht/EQ/at/impact/an/6/","d":{"dim1":0,"dim2":1,"dim1Idx":0,"dim2Idx":0},"s":{}}
        out = {'href': app.url_for('location', kwargs['loc']),
               'geomHref': app.url_for('geometry', kwargs['loc']),
               'ac': self.get_context_url(**kwargs),
               'gc': self.get_context_url(ht=kwargs['ht']),}
               #'s': {},
               #'d': {}}
        return json.dumps(out)

    def get_context_data(self, *args, **kwargs):
        ctx = super(PDFReportView, self).get_context_data(*args, **kwargs)

        r = self.request
        randomizer = self.request.GET.get('r') or ''
        ctx['app'] = app = self.get_app()
        ctx['kwargs'] = k = self.kwargs
        report_uri = app.url_for('index')
        client_kwargs = k.copy()
        client_kwargs.pop('app', None)
        context = self.get_context_url(_full=True, **k)
        ctx['context'] = {'url': context,
                          'parts': self.get_further_resources_inputs(**k)}
        fr_map = self.get_further_resources(inputs=ctx['context']['parts'], **k)
        further_resources = []
        for fr_key, fr_list in fr_map.items():
            for fr_item in fr_list:
                # we could do it with set(), but we want to preserve order
                if fr_item in further_resources:
                    continue
                further_resources.append(fr_item)
        ctx['context']['further_resources'] = further_resources

        ctx['risk_analysis'] = risk_analysis = RiskAnalysis.objects.get(id=k['an'])

        def p(val):
            # for test we need full fs path
            if settings.TEST:
                return default_storage.path(val)
            # otherwise, we need nice absolute url
            _path = default_storage.url(val)
            return r.build_absolute_uri(_path)
        ctx['paths'] = {'map': p(os.path.join(context, 'map_{}.png'.format(randomizer) if randomizer else 'map.png')),
                        'charts': [],
                        'legend': p(os.path.join(context, 'legend_{}.png'.format(randomizer) if randomizer else 'legend.png'))}
        
        for cidx in range(0, 4):
            chart_path = os.path.join(context, 'chart_{}_{}.png'.format(cidx, randomizer) if randomizer else 'chart_{}.png'.format(cidx))
            if not os.path.exists(default_storage.path(chart_path)):
                continue
            chart_f = p(chart_path)
            ctx['paths']['charts'].append(chart_f)

        ctx['resources'] = {}
        ctx['resources']['permalink'] =  '{}?init={}'.format(r.build_absolute_uri(report_uri), self.get_client_url(app, **client_kwargs))

        for resname in ('permalink', 'dims', 'dimsVal',):
            _fname = os.path.join(context, '{}_{}.txt'.format(resname, randomizer) if randomizer else '{}.txt'.format(resname))
            fname = default_storage.path(_fname)
            if os.path.exists(fname):
                with open(fname, 'rt') as f:
                    data = json.loads(f.read())
                    ctx['resources'][resname] = data

        ctx['dimensions'] = self.get_dimensions(risk_analysis, ctx['resources'])
        return ctx

    def get_dimensions(self, risk_analysis, selected):
        dims = selected['dims']
        dimsVal = selected['dimsVal']
        headers = []
        _values = []

        def make_selected(r, sel):
            r.selected = r.value == sel
            return r

        for didx, dname in enumerate(dims):
            dselected = dimsVal[didx]
            di = risk_analysis.dymensioninfo_set.filter(name=dname).distinct().first()
            headers.append(di)
            rows = [make_selected(r, dselected) for r in risk_analysis.dymensioninfo_associacion.filter(dymensioninfo=di)]
            _values.append(rows)
            
        values = zip(*_values)
        return {'headers': headers,
                'values': values}

    def get_document_urls(self, app, randomizer):
        out = []
        r = self.request
        k = self.kwargs.copy()
        for part in self.PDF_PARTS:
            if part != 'report':
                continue
            k['pdf_part'] = part
            out.append(r.build_absolute_uri('{}?r={}'.format(app.url_for('pdf_report_part', **k), randomizer)))

        return out

    def get_template_names(self):
        app = self.get_app()
        pdf_part = self.kwargs['pdf_part']
        out = [self.TEMPLATE_NAME.format(app.name, pdf_part)]
        return out

    def form_invalid(self, form):
        out = {'succes': False, 'errors': form.errors}
        log.error("Cannot generate pdf: %s: %s", self.request.build_absolute_uri(), form.errors)
        return json_response(out, status=400)

    def form_valid(self, form):
        ctx = self.get_context_url(_full=True, **self.kwargs)

        r = self.request
        out = {'success': True}
        app = self.get_app()
        config = {}

        randomizer = get_random_string(7)
        cleanup_paths = []
        for k, v in form.cleaned_data.iteritems():
            if v is None:
                continue
            if not isinstance(v, File):
                target_path = os.path.join(ctx, '{}_{}.txt'.format(k, randomizer))
                v = ContentFile(json.dumps(v))
                target_path = default_storage.save(target_path, v)
                cleanup_paths.append(default_storage.path(target_path))
                
            else:
                basename, ext = os.path.splitext(v.name)
                target_path = os.path.join(ctx, '{}_{}.png'.format(k, randomizer))
                target_path = default_storage.save(target_path, v)
                cleanup_paths.append(default_storage.path(target_path))

            if settings.TEST:
                full_path = default_storage.path(target_path)
                target_path = full_path
            else:
                target_path = default_storage.url(target_path)

            config[k] = target_path

        pdf_path = default_storage.path(os.path.join(ctx, 'report_{}.pdf'.format(randomizer)))
        cleanup_paths.append(pdf_path)
        config['pdf'] = pdf_path
        config['urls'] = self.get_document_urls(app, randomizer)

        pdf = generate_pdf(**config)
        out['pdf'] = pdf

        def cleanup():
            self.cleanup(cleanup_paths)

        with open(pdf, 'rb') as fd:
            data = fd.read()


        resp = HttpResponse(data, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="report.pdf"'
        cleanup()
        return resp

        #return CleaningFileResponse(f, on_close=cleanup)

    def cleanup(self, paths):
        for path in paths:
            if os.path.exists(path):
                try:
                    os.unlink(path)
                except OSError, err:
                    print('error when removing', path, err)

    def render_report_markup(self, ctx, request, *args, **kwargs):

        html_path = os.path.join(ctx, 'template.html')
        html_path_absolute = default_storage.path(html_path)

        pdf_ctx = self.get_context_data(*args, **kwargs)
        html_template = self.get_template_names()[0]
        tmpl = render_to_string(html_template, pdf_ctx, request=self.request)
        default_storage.save(html_path, ContentFile(tmpl))

        return html_path_absolute