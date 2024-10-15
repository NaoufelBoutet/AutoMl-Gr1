from django.http import HttpResponse
from django.shortcuts import render , redirect
from Exploration_donnees.models import Utilisateurs
import csv
#from django.contrib import messages
from .models import Projet
from .forms import ProjetForm
import os  # Nécessaire pour gérer les chemins de fichiers


def hello(request):
    utilisateurs = Utilisateurs.objects.all()
    return render(request, 'Exploration_donnees/hello.html', {'utilisateurs': utilisateurs})

from django.contrib import messages

def import_csv(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST, request.FILES)
        if form.is_valid():
            projet = form.save()
            messages.success(request, 'Fichier téléchargé avec succès')
            csv_path = projet.csv_file.path
            if not csv_path.endswith('.csv'):
                messages.error(request, 'Ce fichier n\'est pas un fichier CSV.')
                return redirect('import_csv')
            try:
                with open(csv_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)
                    for row in reader:
                        print(f"Nom du projet : {row[0]}")
                messages.success(request, 'Fichier CSV importé avec succès !')
                return redirect('import_csv')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'importation : {str(e)}')
                return redirect('import_csv')
    else:
        form = ProjetForm()

    return render(request, 'import_csv.html', {'form': form})

# a faire : 

def contact_us(request):
    return HttpResponse(" Voici un formulaire de contact.")

def about_us(request):
    return HttpResponse('<h1>À propos de nous </h1> <p>Nous adorons les graphs, les statistiques et les modeles</p>')

def help(request):
    return HttpResponse(" Aide et Exemples.")