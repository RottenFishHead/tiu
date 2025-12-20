from django import forms
from .models import Task, Appointment

class TaskForm(forms.ModelForm):
    
    due = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
     
    class Meta:
        model = Task
        fields = ['title', 'complete', 'due', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'complete': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add any additional notes here...'
            })
        }
        labels = {
            'title': 'Task Title',
            'complete': 'Mark as Complete',
            'due': 'Due Date',
            'notes': 'Notes'
        }


class AppointmentForm(forms.ModelForm):
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
     
    class Meta:
        model = Appointment
        fields = ['title', 'complete', 'date', 'time', 'location', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter appointment title'
            }),
            'complete': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter location (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add any additional notes here...'
            })
        }
        labels = {
            'title': 'Appointment Title',
            'complete': 'Mark as Complete',
            'date': 'Date',
            'time': 'Time',
            'location': 'Location',
            'notes': 'Notes'
        }