from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from poker.models import PokerSession
from .fields import CARD_CHOICES, POSITION_CHOICES, IMAGE_CHOICES, STACK_CHOICES, RESULTS_CHOICES, \
    ACTION_CHOICES



class Hands(models.Model):
    session = models.ForeignKey(PokerSession, on_delete=models.CASCADE, related_name='session')
    hero = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hero')
    result = models.CharField(max_length=4, choices=RESULTS_CHOICES)
    effective = models.CharField(max_length=30, choices=STACK_CHOICES)
    hero_card_1 = models.CharField(max_length=30, choices=CARD_CHOICES)
    hero_card_2 = models.CharField(max_length=30, choices=CARD_CHOICES)
    villian_card_1 = models.CharField(max_length=30, choices=CARD_CHOICES)
    villian_card_2 = models.CharField(max_length=30, choices=CARD_CHOICES)
    hero_position = models.CharField(max_length=30, choices=POSITION_CHOICES)
    villian_position = models.CharField(max_length=30, choices=POSITION_CHOICES)
    villian_image = models.CharField(max_length=50, choices=IMAGE_CHOICES)
    hero_stack = models.CharField(max_length=30, choices=STACK_CHOICES)
    villian_stack = models.CharField(max_length=30, choices=STACK_CHOICES)
    preflop_action_h = models.CharField(max_length=40, choices=ACTION_CHOICES, verbose_name='Hero Preflop')
    flop_action_h= models.CharField(max_length=40, choices=ACTION_CHOICES,blank=True, null=True, verbose_name='Hero Flop')
    turn_action_h= models.CharField(max_length=40, choices=ACTION_CHOICES,blank=True, null=True, verbose_name='Hero Turn')
    river_action_h = models.CharField(max_length=40, choices=ACTION_CHOICES,blank=True, null=True, verbose_name='Hero River')
    preflop_action_v = models.CharField(max_length=40, choices=ACTION_CHOICES, verbose_name='Villian Preflop')
    flop_action_v = models.CharField(max_length=40, choices=ACTION_CHOICES,blank=True, null=True, verbose_name='Villian Flop')
    turn_action_v = models.CharField(max_length=40, choices=ACTION_CHOICES,blank=True, null=True, verbose_name='Villian Turn')
    river_action_v = models.CharField(max_length=40, choices=ACTION_CHOICES,blank=True, null=True, verbose_name='Villian River')
    preflop_bet_h = models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    flop_bet_h= models.DecimalField(decimal_places=2,  max_digits=6, blank=True, null=True)
    turn_bet_h= models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    river_bet_h = models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    preflop_bet_v = models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    flop_bet_v = models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    turn_bet_v = models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    river_bet_v = models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    preflop_callers = models.DecimalField(decimal_places=0, max_digits=1, blank=True, null=True)
    flop_callers = models.DecimalField(decimal_places=0, max_digits=1, blank=True, null=True)
    turn_callers = models.DecimalField(decimal_places=0, max_digits=1, blank=True, null=True)
    river_callers = models.DecimalField(decimal_places=0, max_digits=1, blank=True, null=True)
    flop1 = models.CharField(max_length=30, choices=CARD_CHOICES,blank=True, null=True)
    flop2 = models.CharField(max_length=30, choices=CARD_CHOICES,blank=True, null=True)
    flop3 = models.CharField(max_length=30, choices=CARD_CHOICES,blank=True, null=True)
    turn = models.CharField(max_length=30, choices=CARD_CHOICES, blank=True, null=True)
    river = models.CharField(max_length=30, choices=CARD_CHOICES, blank=True, null=True)
    notes = models.TextField(max_length=5000, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return str(self.title)
    
    def get_absolute_url(self):
        return reverse("hands:hand_detail", kwargs={"id":self.id})
