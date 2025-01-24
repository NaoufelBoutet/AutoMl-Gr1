from django import forms
from django.core.exceptions import ValidationError

class UploadFileForm(forms.Form):
    csv_file = forms.FileField()

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file', None)

        if csv_file:
            # Vérifie si l'extension est valide (.csv ou .txt)
            if not (csv_file.name.endswith('.csv') or csv_file.name.endswith('.txt')):
                raise ValidationError('Le fichier doit être au format CSV ou TXT.')

            # Vérifie si la longueur du nom du fichier est correcte
            if len(csv_file.name) > 50:
                raise ValidationError("Le nom du fichier ne doit pas dépasser 50 caractères.")

        return csv_file