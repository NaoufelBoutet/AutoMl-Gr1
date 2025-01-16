from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import pandas as pd
from . import forms
from . import bddMongoCon

@login_required
def accueil(request):
    MongoDict = bddMongoCon.MongoConnexion()

    # Récupérer les datasets de l'utilisateur
    datasets = MongoDict["coll"].find({'user_id': request.user.id})
    dataset_list = [dataset['dataset_name'] for dataset in datasets]

    if request.method == 'POST':
        form = forms.FileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES['file']
            dataset_name = form.cleaned_data.get('dataset_name', uploaded_file.name)
            separator = form.cleaned_data.get('separator', ',')
            file_size = uploaded_file.size

            # Vérifier la taille du fichier
            if file_size > 5 * 1024 * 1024:
                form.add_error('file', 'La taille du fichier ne doit pas dépasser 5 Mo.')
                return render(request, 'accueil.html', {'form': form, 'dataset_list': dataset_list})

            # Vérifier si le dataset_name existe déjà avant de lire le fichier
            existing_dataset = MongoDict["coll"].find_one({'user_id': request.user.id, 'dataset_name': dataset_name})
            if existing_dataset:
                form.add_error('file', 'Un dataset avec ce nom existe déjà.')
                return render(request, 'accueil.html', {'form': form, 'dataset_list': dataset_list})

            try:
                # Lire le fichier avec pandas
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, sep=separator)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                elif uploaded_file.name.endswith('.xls'):
                    df = pd.read_excel(uploaded_file, engine='xlrd')
                else:
                    form.add_error('file', 'Format de fichier non supporté.')
                    return render(request, 'accueil.html', {'form': form, 'dataset_list': dataset_list})

                # Convertir le DataFrame en dictionnaire pour l'insérer dans MongoDB
                data_dict = df.to_dict("records")
                column_names = df.columns.tolist()

                # Vérification si les données sont bien lues
                if not data_dict:
                    form.add_error('file', 'Aucune donnée n\'a été lue à partir du fichier.')
                    return render(request, 'accueil.html', {'form': form, 'dataset_list': dataset_list})

                organized_data = {
                    'user_id': request.user.id,
                    'dataset_name': dataset_name,
                    'columns': column_names,
                    'data': data_dict
                }

                # Enregistrer les données dans MongoDB
                MongoDict['db'].Datas.insert_one(organized_data)

            except Exception as e:
                form.add_error('file', f'Erreur lors de la lecture ou de l\'insertion : {str(e)}')
                return render(request, 'accueil.html', {'form': form, 'dataset_list': dataset_list})

            return redirect('accueil')

    else:
        form = forms.FileUploadForm()

    MongoDict['client'].close()
    return render(request, 'accueil.html', {'form': form, 'dataset_list': dataset_list})
@login_required
def afficher_dataset(request):
    MongoDict = bddMongoCon.MongoConnexion()
    if request.method == 'POST':
        dataset_name = request.POST.get('dataset')
        if dataset_name:
            dataset = MongoDict["coll"].find_one({'user_id': request.user.id, 'dataset_name': dataset_name})

            if dataset:
                
                df = pd.DataFrame(dataset['data'])
                
                request.session['dataset'] = df.to_json()

                missing_values = df.isnull().sum().to_dict()
                
                describe_stats = df.describe().T
                
                column_types = df.dtypes.apply(str).to_dict()
               
                # Récupérer les colonnes
                columns = dataset['columns'] if 'columns' in dataset else []

                # Renvoie la liste complète des datasets
                
                return render(request, 'accueil.html', {
            'form': forms.FileUploadForm(),  
            'dataset': dataset['data'], 
            'columns': columns,
            'dataset_name': dataset_name,  
            'dataset_list': [ds['dataset_name'] for ds in MongoDict["coll"].find({'user_id': request.user.id})],
            'missing_values': missing_values,
            'describe_stats': describe_stats,
            'column_types': column_types,
        })
    MongoDict['client'].close()
    return redirect('accueil')

@login_required
def supprimer_dataset(request):
    if request.method == 'POST':
        dataset_name = request.POST.get('dataset_name')
        
        if dataset_name:
            MongoDict = bddMongoCon.MongoConnexion()

            # Supprimer le dataset de la base de données
            result = MongoDict["coll"].delete_one({'user_id': request.user.id, 'dataset_name': dataset_name})
            
            
            MongoDict['client'].close()

        return redirect('accueil')  
    
@login_required   
def nettoyage_dataset(request):
    if request.method == "POST":
        dataset_json = request.session.get('dataset')
        dataset = pd.read_json(dataset_json)
        print(dataset)
        
        
        return render(request, 'data_cleanning.html',{"dataset":dataset})
      