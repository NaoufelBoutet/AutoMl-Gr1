from django.shortcuts import render, redirect
import csv
from utils import get_db_mongo
import pymongo
import gridfs
from django.urls import reverse
import pandas as pd
from io import BytesIO
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib import messages
from . import forms


@login_required
def accueil(request):
     return render(request, "accueil.html")


@login_required
def create_project(request):
    if request.method == 'POST':
        db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
        col = db["User"]
        project_name = request.POST.get('project_name')
        user_id = str(request.user.id)
        user_name = request.user.username
        user_doc = col.find_one({'_id': user_id})
        if not user_doc:
            print(f"Utilisateur {user_id} non trouvé, création d'un nouveau document")
            new_user = {
                '_id': user_id,
                'username': user_name,
                'projects': []
            }
            col.insert_one(new_user)
            user_doc = new_user  
        existing_project = next((project for project in user_doc['projects'] if project['name'] == project_name), None)
        if existing_project:
            messages.error(request, f"Le projet '{project_name}' existe déjà.")
            return redirect('accueil')
        new_project = {  
            'name': project_name,
            'data': []
        }
        col.update_one(
            {'_id': user_id},
            {'$push': {'projects': new_project}}
        )
        client.close()
        messages.success(request, f"Le projet '{project_name}' a été créé avec succès.")
        return render(request, 'accueil.html')

    return render(request, 'accueil.html')


@login_required
def projects(request):
    db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
    col = db["User"]
    user_id = str(request.user.id)
    user_doc = col.find_one({'_id': user_id})
    if user_doc:
        projects = user_doc.get('projects', [])
    else:
        projects = []
    client.close()
    return render(request, 'projet.html', {'projects': projects})


@login_required
def projet_data(request):
    if request.method == 'POST':  
        db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
        col = db["User"]
        user_id = str(request.user.id)
        project_name = request.POST.get('projet_name')  
        user_doc = col.find_one({'_id': user_id})
        projects = user_doc.get('projects', [])
        project = next((p for p in projects if p['name'] == project_name), None)
        client.close()
        dataset_names = [dataset['dataset_name'] for dataset in project.get('data', [])]
        return render(request, 'projet_dataset.html',{'project_name':project_name,"dataset_names":dataset_names})
    return redirect('upload_fichier')  




@login_required
def upload_fichier(request):
    if request.method == 'POST':
        project_name = request.POST.get('projet_name')
        print(project_name)
        db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
        col = db["User"]
        user_id = str(request.user.id)
        user_doc = col.find_one({'_id': user_id})
        projects = user_doc.get('projects', [])
        project = next((p for p in projects if p['name'] == project_name), None)
        dataset_names = [dataset['dataset_name'] for dataset in project.get('data', [])]
        separator = request.POST.get('separator', ',')  
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            file_size = uploaded_file.size
            if file_size > 15 * 1024 * 1024:  
                messages.error(request, "La taille du fichier ne doit pas dépasser 5 Mo.")
                return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, sep=separator)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                elif uploaded_file.name.endswith('.xls'):
                    df = pd.read_excel(uploaded_file, engine='xlrd')
                else:
                    messages.error(request, "Format de fichier non supporté.")
                    return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})
                data_dict = df.to_dict("records")
                if not data_dict:
                    messages.error(request, "Aucune donnée n'a été lue à partir du fichier.")
                    return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})
                dataset_name = uploaded_file.name  
                existing_dataset = next((dataset for dataset in project.get('data', []) if dataset['dataset_name'] == dataset_name), None)
                if existing_dataset:
                    messages.error(request, "Un dataset avec ce nom existe déjà dans ce projet.")
                    return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})
                organized_data = {
                    'dataset_name': dataset_name,
                    'data': data_dict
                }
                col.update_one(
                    {'_id': user_id, 'projects.name': project_name},
                    {'$push': {'projects.$.data': organized_data}}
                )
                user_doc = col.find_one({'_id': user_id})
                projects = user_doc.get('projects', [])
                project = next((p for p in projects if p['name'] == project_name), None)
                dataset_names = [dataset['dataset_name'] for dataset in project.get('data', [])]
                client.close()
                messages.success(request, f"Le fichier a été téléchargé avec succès dans le projet {project_name}.")
                return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})
            except Exception as e:
                messages.error(request, f"Erreur lors du traitement du fichier : {str(e)}")
                return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})
        else:
            messages.error(request, "Aucun fichier n'a été téléchargé.")
            return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})

    return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})




@login_required
def dataset_info(request):
    if request.method == "POST":
        project_name = request.POST.get('project_name')
        dataset_name = request.POST.get('selected_dataset')
        action = request.POST.get('action')
        db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
        col = db["User"]
        user_id = str(request.user.id)
        user_doc = col.find_one({'_id': user_id})
        projects = user_doc.get('projects', [])
        project = next((p for p in projects if p['name'] == project_name), None)
        dataset_names = [dataset['dataset_name'] for dataset in project.get('data', [])]
        dataset = next((d for d in project.get('data', []) if d['dataset_name'] == dataset_name), None)
        if action == "action1":
            try:
                df = pd.DataFrame(dataset['data'])
                ligne = df.shape[0]  
                colonne = df.shape[1]  
                nb_nul = df.isnull().sum().to_frame(name="Nombre de valeurs nulles").to_html(classes="table table-bordered") 
                nb_colonne_double = df.duplicated().sum()  
                table_html=df.to_html(classes='display',table_id="dataframe-table",index=False)
                client.close()
                return render(request, 'projet_dataset.html', {'table_html':table_html,
                    'dataset_name': dataset_name,
                    "dataset_names":dataset_names,
                    'ligne': ligne,
                    'colonne': colonne,
                    'nb_nul': nb_nul,
                    'nb_colonne_double': nb_colonne_double,
                    "project_name":project_name
                })
            except Exception as e:
                messages.error(request, f"Erreur lors de l'analyse du dataset : {str(e)}")
                client.close()
                return render(request,'projet_dataset.html',{"project_name":project_name,'dataset_name': dataset_name,'dataset_name':dataset_name})
        elif action == "action2":
            return render(request,'nettoyage.html',{"project_name":project_name,"dataset_name":dataset_name,'dataset_name':dataset_name})
    else:
        return render(request,'projet_dataset.html',{"project_name":project_name,'dataset_name': dataset_name,'dataset_name':dataset_name})

def cleanning(request):
     if request.method == "POST":
        project_name = request.POST.get('project_name')
        dataset_name = request.POST.get('dataset_name')
        db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
        col = db["User"]
        user_id = str(request.user.id)
        user_doc = col.find_one({'_id': user_id})
        projects = user_doc.get('projects', [])
        project = next((p for p in projects if p['name'] == project_name), None)
        dataset_names = [dataset['dataset_name'] for dataset in project.get('data', [])]
        return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})


  




