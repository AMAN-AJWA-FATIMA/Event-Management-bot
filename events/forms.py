from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'start_date', 'end_date', 'max_participants']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
