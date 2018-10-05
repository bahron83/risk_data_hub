from django.core.management.base import BaseCommand
import os
from django.db import models
from risks.models import Event


class Command(BaseCommand):
    def handle(self, **options):
        with open('/home/geo/my_ids.txt', 'r') as f:
            content = f.readlines()
        with open('/home/geo/my_res.csv', 'w') as r:
            for line in content:
                ids = line.replace('\r\n', '').split(',')                
                matches = Event.objects.filter(pk__in=ids)                
                for m in matches:                    
                    r.write('\t'.join([m.event_id, m.iso2, m.nuts3, m.begin_date.strftime('%Y-%m-%d'), m.sources]) + "\n")
