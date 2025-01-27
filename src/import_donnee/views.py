from django.shortcuts import render, redirect
import csv
from utils import get_db_mongo
import pymongo
import gridfs
from django.urls import reverse
from io import BytesIO
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib import messages
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder,MinMaxScaler, RobustScaler, MinMaxScaler
from sklearn.model_selection import train_test_split



@login_required
def accueil(request):
    col, client = get_db_mongo()
    user_id = str(request.user.id)
    user_doc = col.find_one({'_id': user_id})
    project_names = [project['name'] for project in user_doc.get('projects', [])] if user_doc else []
    client.close()
    
    return render(request, 'accueil.html', {'project_names': project_names})


@login_required
def create_project(request):
    if request.method == 'POST':
        col, client = get_db_mongo()
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
        return redirect('accueil')

    return render(request, 'accueil.html')

@login_required
def delete_project(request):
    if request.method == 'POST':
        col, client = get_db_mongo()
        project_name = request.POST.get('project_name')
        user_id = str(request.user.id)
        col.update_one(
            {'_id': user_id},
            {'$pull': {'projects': {'name': project_name}}})
        client.close()
        messages.success(request, f"Le projet '{project_name}' a été supprimé avec succès.")
        return redirect('accueil')


@login_required
def projects(request):
    col, client = get_db_mongo()
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
        col, client = get_db_mongo()
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
        col, client = get_db_mongo()
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
        col, client = get_db_mongo()
        user_id = str(request.user.id)
        user_doc = col.find_one({'_id': user_id})
        projects = user_doc.get('projects', [])
        project = next((p for p in projects if p['name'] == project_name), None)
        dataset_names = [dataset['dataset_name'] for dataset in project.get('data', [])]
        dataset = next((d for d in project.get('data', []) if d['dataset_name'] == dataset_name), None)
        data = dataset.get('data', [])
        df = pd.DataFrame(data)
        columns = df.columns
        column_types = df.dtypes.apply(lambda x: x.name).to_dict()
        columns_with_types = [(col, column_types[col]) for col in columns]
        object_columns = [col for col, col_type in columns_with_types if col_type == "object"]
        numeric_columns = [col for col, col_type in df.dtypes.items() if col_type in ['int64', 'float64']]
        encoding_methods_numerique = [("robust", "RobustScaler"), ("standard", "StandardScaler"),("minmax","MinMaxScaler")]
        encoding_methods = [("onehot", "One-Hot Encoding"), ("label", "Label Encoding")]
        if action == "action1" or action == "action5":
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
                    "project_name":project_name,
                    "numeric_columns":numeric_columns,
                })
            except Exception as e:
                messages.error(request, f"Erreur lors de l'analyse du dataset : {str(e)}")
                client.close()
                return render(request,'projet_dataset.html',{"project_name":project_name,'dataset_name': dataset_name,'dataset_names':dataset_names})
        elif action == "action2":
            return render(request,'nettoyage.html',{"encoding_methods_numerique":encoding_methods_numerique,
                                                    "encoding_methods":encoding_methods,
                                                    "numeric_columns":numeric_columns,
                                                    "object_columns":object_columns,   
                                                    "columns_with_types":columns_with_types,
                                                    "columns":columns,"project_name":project_name,
                                                    "dataset_name":dataset_name,
                                                    'dataset_names':dataset_names})
        elif action == "action3":
            col.update_one(
            {'_id': user_id, 'projects.name': project_name},
            {'$pull': {'projects.$.data': {'dataset_name': dataset_name}}})
            user_doc = col.find_one({'_id': user_id})
            projects = user_doc.get('projects', [])
            project = next((p for p in projects if p['name'] == project_name), None)
            dataset_names = [dataset['dataset_name'] for dataset in project.get('data', [])]
            client.close()
            messages.success(request, f"Le dataset '{dataset_name}' a été supprimé avec succès.")
            return render(request, 'projet_dataset.html', {"project_name": project_name, "dataset_names": dataset_names})
        elif action == "action4":
            return render(request,'visualisation.html',{"project_name":project_name,'dataset_name': dataset_name,'dataset_names':dataset_names})
            
    else:
        return render(request,'projet_dataset.html',{"project_name":project_name,'dataset_name': dataset_name,'dataset_names':dataset_names})

def cleanning(request):
     if request.method == "POST":
        project_name = request.POST.get('project_name')
        dataset_name = request.POST.get('dataset_name')
        col, client = get_db_mongo()
        user_id = str(request.user.id)
        user_doc = col.find_one({'_id': user_id})
        projects = user_doc.get('projects', [])
        project = next((p for p in projects if p['name'] == project_name), None)
        dataset_names = [dataset['dataset_name'] for dataset in project.get('data', [])]
        return render(request,'projet_dataset.html',{"project_name":project_name,"dataset_names":dataset_names})


@login_required
def imputation(request):
    if request.method == "POST":
        project_name = request.POST.get('project_name')
        dataset_name = request.POST.get('dataset_name')
        column = request.POST.get('column',None)
        strategy = request.POST.get('strategy', None)
        action = request.POST.get('action')
        replace_value = request.POST.get('replace_value', None)
        old_value = request.POST.get('old_value', None)
        new_value = request.POST.get('new_value', None)
        selected_columns_encod_cat = request.POST.getlist("columns_cat",None)
        selected_columns_encod_num = request.POST.getlist("columns_num",None)
        encoding_method = request.POST.get("encoding_method", None)
        print("project_name",project_name)
        print("dataset_name",dataset_name)
        print("column",column)

        print("strategy",strategy)
        print("action",action)
        print("replace_value",replace_value)
        print("old_value",old_value)
        print("new_value",new_value)
        print("selected_columns_encod_cat",selected_columns_encod_cat)
        print("selected_columns_encod_num",selected_columns_encod_num)
        print("encoding_method",encoding_method)
        col, client = get_db_mongo()
        user_id = str(request.user.id)
        user_doc = col.find_one({'_id': user_id})
        projects = user_doc.get('projects', [])
        project = next((p for p in projects if p['name'] == project_name), None)
        datasets = project.get('data', [])
        dataset = next((d for d in datasets if d['dataset_name'] == dataset_name), None)
        data = dataset.get('data', [])
        df = pd.DataFrame(data)
        columns = df.columns
        column_types = df.dtypes.apply(lambda x: x.name).to_dict()
        columns_with_types = [(col, column_types[col]) for col in columns]
        object_columns = [col for col, col_type in columns_with_types if col_type == "object"]
        numeric_columns = [col for col, col_type in df.dtypes.items() if col_type in ['int64', 'float64']]
        encoding_methods = [("onehot", "One-Hot Encoding"), ("label", "Label Encoding")]
        encoding_methods_numerique = [("robust", "RobustScaler"), ("standard", "StandardScaler"),("minmax","MinMaxScaler")]
        print("columns",columns)
        print("column_types",column_types)
        print("columns_with_types",columns_with_types)
        print("numeric_columns",numeric_columns)
        print("object_columns",object_columns)
        print("encoding_methods",encoding_methods)
        if action == "action1":
            df = drop_doublons(df)
            messages.success(request, f"Les doublons ont été supprimés avec succès.")
        if action == "action2":
            df = valeurs_manquantes(df, column, strategy,replace_value)
            messages.success(request, f"Les valeurs manquantes ont été imputées avec succès.")
        if action == "action3":
            df,message = replace(df,column,old_value,new_value)
            messages.success(request, message)
        if action == "action4":
            df,message = encode_categorical(df, selected_columns_encod_cat, encoding_method)
            messages.success(request, message)
        if action == "action5":
            df,message = encode_numeric(df, selected_columns_encod_num, encoding_method)
            messages.success(request, message)
            
            
            
        col.update_one(
            {'_id': user_id, 'projects.name': project_name, 'projects.data.dataset_name': dataset_name},
            {'$set': {'projects.$.data.$[elem].data': df.to_dict('records')}},
            array_filters=[{"elem.dataset_name": dataset_name}]
        )

        
        client.close()
        return render(request, 'nettoyage.html', {"encoding_methods_numerique":encoding_methods_numerique,
                                                  "encoding_methods":encoding_methods,
                                                  "object_columns":object_columns,
                                                  "numeric_columns":numeric_columns,
                                                  "project_name": project_name, 
                                                  "dataset_name": dataset_name, 
                                                  "columns_with_types": columns_with_types,
                                                  "action":action})

def valeurs_manquantes(df, col, missing_strategy,replace_value):
    if missing_strategy == "mean":
        df[col].fillna(df[col].mean(), inplace=True)
    elif missing_strategy == "median":
        df[col].fillna(df[col].median(), inplace=True)
    elif missing_strategy == "mode":
        df[col].fillna(df[col].mode()[0], inplace=True)
    elif missing_strategy == "drop":
        df.dropna(subset=[col], inplace=True)
    elif missing_strategy == "replace" and replace_value is not None:
        df[col].fillna(replace_value, inplace=True)
    return df


def drop_doublons(df):
    df =df.drop_duplicates()
    return df

def magic_clean(df):
    """
    Nettoie et prépare les colonnes de type 'object' dans un DataFrame.
    """
    for col in df.select_dtypes(include=['object']).columns:
        # Supprime les caractères non imprimables et les espaces inutiles
        df[col] = df[col].astype(str).str.replace(r'[\s\x00-\x1F\x7F-\x9F]+', '', regex=True)

        # Remplace les virgules par des points pour les conversions numériques
        df[col] = df[col].str.replace(',', '.', regex=False)

        # Tente de convertir les colonnes en numérique
        try:
            converted = pd.to_numeric(df[col], errors='raise')
            if converted.notna().all():
                # Conversion en int si toutes les valeurs sont des entiers, sinon en float
                try:
                    df[col] = converted.astype(int)
                except ValueError:
                    df[col] = converted.astype(float)
        except ValueError:
            # Vérifie si la colonne contient des dictionnaires ou des listes
            is_dict = df[col].apply(lambda x: isinstance(x, dict)).all()
            is_list = df[col].apply(lambda x: isinstance(x, list)).all()

            if not (is_dict or is_list):
                # Si ce n'est ni une liste ni un dictionnaire, force en chaîne
                df[col] = df[col].astype(str)
    return df

def replace(df, col, old_value, new_value):
    magic_clean(df)
    col_type = df[col].dtype
    try:
        if pd.api.types.is_numeric_dtype(col_type):
            old_value = float(old_value) if '.' in str(old_value) else int(old_value)
        elif pd.api.types.is_datetime64_any_dtype(col_type):
            old_value = pd.to_datetime(old_value)
        elif pd.api.types.is_bool_dtype(col_type):
            old_value = bool(old_value)
        else:
            old_value = str(old_value)
    except (ValueError, TypeError):
        message = f"Impossible de convertir les valeurs '{old_value}' et '{new_value}' pour correspondre au type '{col_type}'."
    # Vérifie si la valeur à remplacer existe dans la colonne
    if old_value not in df[col].values:
        message =  f"La valeur '{old_value}' n'est pas présente dans la colonne '{col}'."
    else:
        df[col] = df[col].replace(old_value, new_value)
        message = f"Remplacement de '{old_value}' par '{new_value}' effectué avec succès dans la colonne '{col}'."
    return df, message


def encode_categorical(df, col, encoding_method):
 
    if isinstance(col, str):
        col = [col]  
    try:
        if encoding_method == "onehot":
            encoder = OneHotEncoder(sparse_output=False)
            encoded = encoder.fit_transform(df[col])
            encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(col))
            df = df.drop(columns=col).reset_index(drop=True)
            df = pd.concat([df, encoded_df], axis=1)
            message = f"Encodage {encoder.__class__.__name__} effectué avec succès."

        elif encoding_method == "label":
            for column in col:
                le = LabelEncoder()
                df[column] = le.fit_transform(df[column])
                message = f"Encodage {le.__class__.__name__} effectué avec succès."
    except Exception as e:
        message = f"Erreur lors de l'encodage : {str(e)}"
        return df, message
    return df, message
        


def encode_numeric(df,col,encoding_method):
    magic_clean(df)
    print(encoding_method)
    print(col)
    if isinstance(col, str):
        col = [col]
    if encoding_method == "standard":
        scaler = StandardScaler() 
    elif encoding_method == "minmax":
        scaler = MinMaxScaler()
    elif encoding_method == "robust":
        scaler = RobustScaler()
    try:
        encoded = scaler.fit_transform(df[col])
        encoded_df = pd.DataFrame(encoded, columns=scaler.get_feature_names_out(col))
        df = df.drop(columns=col).reset_index(drop=True)
        df = pd.concat([df, encoded_df], axis=1)
    except Exception as e:
        return df ,f'Erreur de l encodage avec {scaler.__class__.__name__}:{e}'
    return df ,f"Encodage {scaler.__class__.__name__} effectué avec succès."
