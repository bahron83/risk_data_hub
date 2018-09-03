from jsonfield import JSONField
import xlrd
from django.db import models
from risks.models import Exportable, RiskApp, RiskAnalysis


class AdditionalData(Exportable, models.Model):
    EXPORT_FIELDS = (('name', 'name',),
                     ('table', 'data',))

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, default='')
    risk_analysis = models.ForeignKey(RiskAnalysis, related_name='additional_data')
    data = JSONField(null=False, blank=False, default={})

    def __str__(self):
        return "Additional Data #{}: {}".format(self.id, self.name)

    @classmethod
    def import_from_sheet(cls, risk, sheet_file, name=None, sheets=None):
        wb = xlrd.open_workbook(filename=sheet_file)
        out = []
        for sheet in wb.sheets():
            col_names = [item.value for item in sheet.row(0)]
            # first row in column 0 belongs to column names
            row_names = [item.value for item in sheet.col(0)[1:]]

            values = []
            for rnum in range(1, sheet.nrows):
                values.append([item.value for item in sheet.row(rnum)[1:]])

            data = {'column_names': col_names,
                    'row_names': row_names,
                    'values': values}

            ad = cls.objects.create(name=sheet.name, risk_analysis=risk, data=data)
            out.append(ad)
        return out

def create_risks_apps(apps, schema_editor):
    RA = apps.get_model('risks', 'RiskApp')
    for rname, rlabel in RiskApp.APPS:
        RA.objects.get_or_create(name=rname)

def uncreate_risks_apps(apps, schema_editor):
    RA = apps.get_model('risks', 'RiskApp')
    RA.objects.all().delete()

def get_risk_app_default():
    return RiskApp.objects.get(name=RiskApp.APP_DATA_EXTRACTION).id