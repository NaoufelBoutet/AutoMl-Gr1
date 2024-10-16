from django import forms
from django.core.exceptions import ValidationError

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
    def clean_file(self):
        file = self.cleaned_data.get('file', None)
        if file:
            if not file.name.endswith('.csv'):
                raise ValidationError('Ce fichier n\'est pas un fichier CSV valide.')
        return file