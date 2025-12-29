from django import forms


POSITION_CHOICES = (
    ('SB', 'SB'),
    ('BB', 'BB'),
    ('UTG', 'UTG'),
    ('UTG1', 'UTG+1'),
    ('UTG2', 'UTG+2'),
    ('LJ', 'LJ'),
    ('HJ', 'HJ'),
    ('CO', 'CO'),
    ('BTN', 'BTN'),
    
)

STAKES_CHOICES = (
    ('00', 'All'),
    ('12', '1/2'),
    ('13', '1/3'),
    ('23', '2/3'),
    ('25', '2/5'),
    ('55', '5/5'),
    ('510', '5/10'),
    ('2040', '20/40'),
)

TYPE_CHOICES = (
    ('BET_SIZE', 'Bet Sizing'),
    ('COP', 'Cop'),
    ('ODDS', 'Odds'),
    ('HAND_SELECT', 'Hand Selection'),
    ('GAME_SELECT','Game Selection'),
    ('OTHER', 'Other'),
)
STREET_CHOICES = (
    ('PREFLOP','Preflop'),
    ('FLOP', 'FLOP'),
    ('TURN', 'Turn'),
    ('RIVER', 'River'),
)

CARD_CHOICES = (
    ('As', 'As'),
    ('2s', '2s'),
    ('3s', '3s'),
    ('4s', '4s'),
    ('5s', '5s'),
    ('6s', '6s'),
    ('7s', '7s'),
    ('8s', '8s'),
    ('9s', '9s'),
    ('10s', '10s'),
    ('Js', 'Js'),
    ('Qs', 'Qs'),
    ('Ks', 'Ks'),
    ('Ah', 'Ah'),
    ('2h', '2h'),
    ('3h', '3h'),
    ('4h', '4h'),
    ('5h', '5h'),
    ('6h', '6h'),
    ('7h', '7h'),
    ('8h', '8h'),
    ('9h', '9h'),
    ('10h', '10h'),
    ('Jh', 'Jh'),
    ('Qh', 'Qh'),
    ('Kh', 'Kh'),
    ('Ad', 'Ad'),
    ('2d', '2d'),
    ('3d', '3d'),
    ('4d', '4d'),
    ('5d', '5d'),
    ('6d', '6d'),
    ('7d', '7d'),
    ('8d', '8d'),
    ('9d', '9d'),
    ('10d', '10d'),
    ('Jd', 'Jd'),
    ('Qd', 'Qd'),
    ('Kd', 'Kd'),
    ('Ac', 'Ac'),
    ('2c', '2c'),
    ('3c', '3c'),
    ('4c', '4c'),
    ('5c', '5c'),
    ('6c', '6c'),
    ('7c', '7c'),
    ('8c', '8c'),
    ('9c', '9c'),
    ('10c', '10c'),
    ('Jc', 'Jc'),
    ('Qc', 'Qc'),
    ('Kc', 'Kc'),
    
)

class EmptyChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), empty_label=None, required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):

        # prepend an empty label if it exists (and field is not required!)
        if not required and empty_label is not None:
            choices = tuple([(u'', empty_label)] + list(choices))

        super(EmptyChoiceField, self).__init__(choices=choices, required=required, widget=widget, label=label,
                                        initial=initial, help_text=help_text, *args, **kwargs)