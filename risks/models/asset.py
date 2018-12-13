from django.db import models
from django.contrib.postgres.indexes import GinIndex
from risks.models import (EntityAbstract, AttributeValueVarchar, AttributeValueText,
                                AttributeValueInt, AttributeValueDecimal, AttributeValueDate)
from risks.models.eav_attribute import entity_types


DEFAULT_ENTITY_TYPE = 'asset'

class AssetAttributeValueVarchar(AttributeValueVarchar):    
    asset = models.ForeignKey('Asset')    

class AssetAttributeValueText(AttributeValueText):    
    asset = models.ForeignKey('Asset')    

class AssetAttributeValueInt(AttributeValueInt):    
    asset = models.ForeignKey('Asset')    

class AssetAttributeValueDecimal(AttributeValueDecimal):    
    asset = models.ForeignKey('Asset')    

class AssetAttributeValueDate(AttributeValueDate):    
    asset = models.ForeignKey('Asset') 

class Asset(EntityAbstract, models.Model):
    id = models.AutoField(primary_key=True)
    entity_type = models.CharField(max_length=20, null=False, choices=entity_types, default=DEFAULT_ENTITY_TYPE)        
    name = models.CharField(max_length=50)    
    owner = models.ForeignKey('Owner')
    category = models.ForeignKey('AssetCategory')
    location = models.ForeignKey('Location')    

    class Meta:
        indexes = [
            GinIndex(
                fields=['details'],
                name='asset_details_gin',
            ),
        ]
    
    def __unicode__(self):
        return u"{0}".format(self.name)   

    def get_attributes_saved(self):
        attributes_saved = []
        attributes_saved += AssetAttributeValueVarchar.objects.filter(asset=self)
        attributes_saved += AssetAttributeValueText.objects.filter(asset=self)
        attributes_saved += AssetAttributeValueInt.objects.filter(asset=self)
        attributes_saved += AssetAttributeValueDecimal.objects.filter(asset=self)
        attributes_saved += AssetAttributeValueDate.objects.filter(asset=self)
        return attributes_saved
    
    def get_extra_inline(self, data_type = None):
        attributes_saved = self.get_attributes_saved()
        return len(Asset.get_attributes(data_type)) - len(attributes_saved) 

class AssetItem(models.Model):
    id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset)
    name = models.CharField(max_length=255)    

    def __unicode__(self):
        return u"{0} - {1}".format(self.asset.name, self.name)

class AssetAttributeValue(models.Model):
    id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset)
    attribute = models.ForeignKey('EavAttribute')
    value = models.CharField(max_length=255)

class MarketValue(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(AssetItem)
    value = models.DecimalField(decimal_places=2, max_digits=10)
    area_code = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)