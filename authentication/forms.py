# forms.py
from django import forms
from .models import Task

class CSVFileForm(forms.Form):
    file = forms.FileField()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'start_date', 'due_date', 'priority', 'status', 'assign_users']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'assign_users': forms.SelectMultiple(),  # or specify another widget as needed
        }