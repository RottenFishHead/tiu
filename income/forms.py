from django import forms
from .models import Income

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['user', 'source', 'amount', 'location', 'created']

class PokerWinningsForm(forms.ModelForm):
    """Specific form for adding poker winnings."""
    class Meta:
        model = Income
        fields = ['amount', 'location', 'created']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount won',
                'step': '0.01'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Casino name or location'
            }),
            'created': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
        labels = {
            'amount': 'Winnings Amount',
            'location': 'Casino/Location',
            'created': 'Date'
        }