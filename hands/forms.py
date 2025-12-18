from django import forms
from .models import Hands
from .fields import CARD_CHOICES, ACTION_CHOICES, POSITION_CHOICES, RESULTS_CHOICES



class HandsForm(forms.ModelForm):
    
    result = forms.ChoiceField(
        choices=RESULTS_CHOICES,
        label='Win/Loss?',
        widget=forms.Select(attrs={'size': 1,
                                   

                                   })                    
                                    )

    hero_card_1 = forms.ChoiceField(
        choices=CARD_CHOICES,
        label='1st Card',
        widget=forms.Select(attrs={'size': 1

                                   })                    
                                    )
    hero_card_2 = forms.ChoiceField(
        choices=CARD_CHOICES,
        label='2nd Card',
        widget=forms.Select(attrs={'size': 1

                                   })                    
                                    )
    hero_position = forms.ChoiceField(
        choices=POSITION_CHOICES,
        label='H Position',
        widget=forms.Select(attrs={'size': 1

                                   })                    
                                    )
    villian_position = forms.ChoiceField(
        choices=POSITION_CHOICES,
        label='V Position',
        widget=forms.Select(attrs={'size': 1

                                   })                    
                                    )
    villian_card_1 = forms.ChoiceField(
        choices=CARD_CHOICES,
        label='1st Card',
        widget=forms.Select(attrs={'size': 1

                                   })                    
                                    )
    villian_card_2 = forms.ChoiceField(
        choices=CARD_CHOICES,
        label='2nd Card',
        widget=forms.Select(attrs={'size': 1

                                   })                    
                                    )
    
    
    
    preflop_action_h =  forms.ChoiceField(
                   label='Hero Action',
                   choices=ACTION_CHOICES,
                   required=False
                  ) 
    preflop_action_v =  forms.ChoiceField(
                   label='Villian Action',
                   choices=ACTION_CHOICES,
                   required=False
                  ) 
    flop_action_h =  forms.ChoiceField(
                   label='Hero Action',
                   choices=ACTION_CHOICES,
                   required=False
                  ) 
    flop_action_v =  forms.ChoiceField(
                   label='Villian Action',
                   choices=ACTION_CHOICES,
                   required=False
                  ) 
    turn_action_h =  forms.ChoiceField(
                   label='Hero Action',
                   choices=ACTION_CHOICES,
                   required=False
                  ) 
    turn_action_v =  forms.ChoiceField(
                   label='Villian Action',
                   choices=ACTION_CHOICES,
                   required=False
                  )
    river_action_h =  forms.ChoiceField(
                   label='Hero Action',
                   choices=ACTION_CHOICES,
                   required=False
                  ) 
    river_action_v =  forms.ChoiceField(
                   label='Villian Action',
                   choices=ACTION_CHOICES,
                   required=False
                  ) 
    
    preflop_bet_h =  forms.DecimalField(
                   label='Hero Bet',
                   required=False
                   
                  ) 
    preflop_bet_v =  forms.DecimalField(
                   label='Villian Bet',
                   required=False
                  ) 
    flop_bet_h =  forms.DecimalField(
                   label='Hero Bet',
                   required=False
                  ) 
    flop_bet_v =  forms.DecimalField(
                   label='Villian Bet',
                   required=False
                  ) 
    turn_bet_h =  forms.DecimalField(
                   label='Hero Bet',
                  required=False
                  ) 
    turn_bet_v =  forms.DecimalField(
                   label='Villian Bet',
                  required=False
                  )
    river_bet_h =  forms.DecimalField(
                   label='Hero Bet',
                  required=False
                  ) 
    river_bet_v =  forms.DecimalField(
                   label='Villian Bet',
                 required=False
                  ) 
    
    class Meta:
        model = Hands
        fields = '__all__'
        

       

