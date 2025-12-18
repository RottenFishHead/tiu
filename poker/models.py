from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from .fields import STAKES_CHOICES
    
class Casino(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)
    

class PokerSession(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player')
    casino = models.ForeignKey(Casino, on_delete=models.CASCADE)
    stakes = models.CharField(max_length=20, choices=STAKES_CHOICES)
    date = models.DateField()
    hours = models.IntegerField() 
    buy_in = models.IntegerField() 
    cash_out = models.IntegerField() 
    notes = models.TextField(max_length=5000, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-date',)
    
    def __str__(self):
        return str(self.id)

    @property
    def win_loss(self):
        return self.cash_out - self.buy_in

    @property
    def win_rate_per_hour(self):
        if self.hours > 0:
            return self.win_loss / self.hours
        return 0
    
    def total_session_hours(self):
        total_hours = (self.clock_out - self.clock_in).seconds // 3600
        if self.break_start and self.break_end:
            break_hours = (self.break_end - self.break_start).seconds // 3600
            total_hours -= break_hours
        return total_hours

