from django.db import models
from django.template.defaultfilters import slugify

class KnownHost(models.Model):
    host = models.CharField(max_length=100)
    port = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('host', 'port', 'username', 'password')
