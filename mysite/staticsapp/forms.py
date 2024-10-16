from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField()
    separator = forms.ChoiceField(choices=[(',', 'Virgule'), (';', 'Point-virgule'), ('\t', 'Tabulation')])