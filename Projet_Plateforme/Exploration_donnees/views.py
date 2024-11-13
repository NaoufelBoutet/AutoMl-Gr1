from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , redirect
from Exploration_donnees.models import Utilisateurs
import csv
from django.contrib import messages
from .models import Projet, ProjetDatasetViewer
from .forms import ProjetForm
import os  # Nécessaire pour gérer les chemins de fichiers
from django.core.mail import send_mail
from django.urls import reverse
import pandas as pd
import xlrd # ouvrir vieux fichier excel xls
import openpyxl # ouvrir fichier excel
from plotly.offline import plot
import plotly.graph_objects as go

#------------------------------------------------------------------
def hello(request):
    utilisateurs = Utilisateurs.objects.all()
    return render(request, 'Exploration_donnees/hello.html', {'utilisateurs': utilisateurs})

#------------------------------------------------------------------

# Vue pour gérer l'importation et l'affichage du fichier
def import_file(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST, request.FILES)
        if form.is_valid():
            projet = form.save()
            messages.success(request, 'Fichier téléchargé avec succès.')
            # Utilisation de la classe ProjetDatasetViewer
            viewer = ProjetDatasetViewer(projet.file.path)
            viewer.load_data()
            data, error = viewer.get_data()
            #data = pd.DataFrame(data)
            print(">>>>>>>>>", data, type(data))
            fig = go.Figure()
            graph =go.Table(
                header=dict(values=data.columns,
                            font=dict(size=15),
                            align="left"), 
                cells=dict(values=[[element for element in data[data.columns[i]]] for i in range(len(data.columns))],
                           font=dict(size=10),
                            align="center"))
            fig.add_trace(graph)
            fig.update_layout(width=1000, height=1000)
            plt_div = plot(fig, output_type="div")
            # Envoyer un email à l'administrateur   
            if error:
                messages.error(request, error)
                return redirect('import_file')
            # Passer les données au template pour affichage
            return render(request, 'import_csv.html', {'form': form, 'data': plt_div, "nom" : data})
    else:
        form = ProjetForm()
    return render(request, 'import_csv.html', {'form': form})
# a faire : 



def analyses(request):
    return render(request, 'analyses.html')
