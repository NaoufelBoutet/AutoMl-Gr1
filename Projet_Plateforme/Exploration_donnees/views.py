from django.http import HttpResponse
from django.shortcuts import render , redirect
from Exploration_donnees.models import Utilisateurs
import csv
#from django.contrib import messages
from .models import Projet
from .forms import ProjetForm


def hello(request):
    utilisateurs = Utilisateurs.objects.all()
    return render(request, 'Exploration_donnees/hello.html',
        {'utilisateurs': utilisateurs})

def import_csv(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.save()
            print('succes')
            # Vérification du type de fichier
            """if not csv_file.nom_projet.endswith('.csv'):
                messages.error(request, 'Ce fichier n\'est pas un fichier CSV.')
                return redirect('import_csv')"""

            # Lire le fichier CSV
            """try:
                reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
                next(reader)  # Ignorer la ligne d'en-tête
                for row in reader:
                    # Assurez-vous que le fichier CSV contient les colonnes nécessaires
                    _, created = Projet.objects.get_or_create(
                        name=row[0],
                    )
                messages.success(request, 'Fichier CSV importé avec succès !')
                return redirect('import_csv')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'importation : {str(e)}')
                return redirect('import_csv')"""
    else:
        form = ProjetForm()

    return render(request, 'import_csv.html', {'form': form})
