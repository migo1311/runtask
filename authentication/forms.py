# forms.py
from django import forms

class CSVFileForm(forms.Form):
    file = forms.FileField()
