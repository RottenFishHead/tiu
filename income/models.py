from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User


#Source is Poker, Ebay, job, etc...
class Source(models.Model):
    name = models.CharField(max_length=75, blank=False, null=False)
    created = models.DateField(default=now)
    
    def __str__(self):
            return self.name
    
class Income(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateField(default=now)
 
    def __init__(self, source):
        self.source = source

    def __str__(self):
        return str(self.source)