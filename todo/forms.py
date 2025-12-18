from django import forms
from .models import Task
from datetime import timedelta

class TaskForm(forms.ModelForm):
    
    due = forms.CharField(widget=forms.TextInput(attrs={'type':'date'}))
     
    class Meta:
        model = Task
        fields = ['category', 'title', 'complete', 'due', 'notes']