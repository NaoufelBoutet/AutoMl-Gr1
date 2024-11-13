
from django import forms
from .models import Projet, ProjetDatasetViewer


# Creer un projet et le nom de projet
class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['nom_Projet', 'file']



