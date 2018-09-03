from django.core.urlresolvers import reverse
from django.db import models


class RiskApp(models.Model):
    APP_DATA_EXTRACTION = 'data_extraction'
    APP_COST_BENEFIT = 'cost_benefit_analysis'
    APP_TEST = 'test'
    APPS = ((APP_DATA_EXTRACTION, 'Data Extraction',),
            (APP_COST_BENEFIT, 'Cost Benefit Analysis',),
            (APP_TEST, 'Test'))    

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, choices=APPS, unique=True, null=False, blank=False)

    def __str__(self):
        return "Risk App: {}".format(self.name)

    @property
    def href(self):
        return self.url_for('index')

    def url_for(self, url_name, *args, **kwargs):
        return reverse('risks:{}:{}'.format(self.name, url_name), args=args, kwargs=kwargs)

    @property
    def description(self):
        n = self.name
        for a in self.APPS:
            if a[0] == n:
                return a[1]
        return n


class RiskAppAware(object):
    def get_url(self, url_name, *args, **kwargs):
        return self.app.url_for(url_name, *args, **kwargs)

    def set_app(self, app):
        """
        Hack for models that don't have app fk (they don't have to)
        """
        self.app = app
        return self