import datetime
from django.utils import timezone
from django.db import models

PROTOCOL_CHOICES = ( 
  ('TCP', 'TCP'),
  ('HTTP', 'HTTP'), 
  ('MYSQL', 'MYSQL') 
) 

class Service(models.Model):
    def __unicode__(self):
        return self.ip + ":" + str(self.port)

    id = models.AutoField (primary_key=True, blank=False)
    ip = models.IPAddressField(blank=False)
    port = models.PositiveSmallIntegerField(blank=False)
    proto = models.CharField(max_length=16, choices=PROTOCOL_CHOICES, default='TCP')
    #performance_warning = models.PositiveIntegerField(default=0)
    #performance_critical = models.PositiveIntegerField(default=3000)
    #availability_critical = models.FloatField(default=0)
    #availability_warning = models.FloatField(default=100)

    def get_fields (self):
        dict = {}
        dict['id'] = self.id
        dict['ip'] = self.ip
        dict['port'] = self.port
        dict['proto'] = self.proto
        #dict['performance_warning'] = self.performance_warning
        #dict['performance_critical'] = self.performance_critical
        #dict['availability_critical'] = self.availability_critical
        #dict['availability_warning'] = self.availability_warning
        return dict

