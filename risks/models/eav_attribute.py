from django.db import models


entity_types = (('asset', 'asset'), ('event', 'event'))
data_types = (('int', 'int'), ('decimal', 'decimal'), ('varchar', 'varchar'), ('text', 'text'), ('date', 'date'))

def resolve_data_type(data_type_name):
    return tuple([t for t in data_types if t[0] == data_type_name])

def get_data_type_string(data_type_name):
    dt = resolve_data_type(data_type_name)
    if dt:
        return dt[0][0]

class EavAttribute(models.Model):
    id = models.AutoField(primary_key=True)
    entity_type = models.CharField(max_length=25, choices=entity_types)
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    data_type = models.CharField(max_length=30, choices=data_types)

    def __unicode__(self):
        return u"{0}".format(self.code)

class AttributeValue(models.Model):
    id = models.AutoField(primary_key=True)        
    attribute = models.ForeignKey('EavAttribute')        

    class Meta:
        abstract = True

class AttributeValueVarchar(AttributeValue):
    data_type = models.CharField(max_length=25, default=get_data_type_string('varchar'))    
    value = models.CharField(max_length=255)

    class Meta:
        abstract = True

class AttributeValueText(AttributeValue):
    data_type = models.CharField(max_length=25, default=get_data_type_string('text'))
    value = models.TextField()

    class Meta:
        abstract = True

class AttributeValueInt(AttributeValue):
    data_type = models.CharField(max_length=25, default=get_data_type_string('int'))
    value = models.IntegerField()

    class Meta:
        abstract = True

class AttributeValueDecimal(AttributeValue):
    data_type = models.CharField(max_length=25, default=get_data_type_string('decimal'))
    value = models.DecimalField(decimal_places=2, max_digits=10)

    class Meta:
        abstract = True

class AttributeValueDate(AttributeValue):
    data_type = models.CharField(max_length=25, default=get_data_type_string('date'))
    value = models.DateField()

    class Meta:
        abstract = True