from django import forms
from django.core.exceptions import ValidationError

class UploadFileForm(forms.Form):
    csv_file = forms.FileField()
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file', None)
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError('Ce fichier n\'est pas un fichier CSV valide.')
        if len(csv_file.name) > 50:
            raise ValidationError("le nom du fichier csv n'est pas validé")
        return csv_file