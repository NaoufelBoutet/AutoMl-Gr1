from django.shortcuts import render, redirect
import csv
from utils import get_db_mongo
import pymongo
import gridfs
from .forms import UploadFileForm
from django.urls import reverse
import pandas as pd
from io import BytesIO
from django.contrib.auth.decorators import login_required
import re
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder,MinMaxScaler
from sklearn.model_selection import train_test_split

@login_required
def home_data(request):
    username=request.user.username
    return render(request, 'home_data.html',{'username' : username})

@login_required
def liste_project(request):
    username = request.user.username
    id = request.user.id   
    list_project = get_project_by_user(username, id)  
    print("1:",list_project)
    if request.method == 'POST':
        action = request.POST.get('action_liste_prj', None)
        projet = request.POST.get('projet', None)
        if action == 'action1':
            delete_project(username, projet)  
            list_project = get_project_by_user(username, id)  
            print("2",list_project)
    return render(request, 'liste_project.html', {'username': username, 'projects': list_project})

@login_required
def project(request,project_name):
    username=request.user.username
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    collection = db['Projet']
    projet=collection.find_one({'username':username,'nom_projet':project_name})
    if not projet :
        id = request.user.id   
        list_project = get_project_by_user(username, id) 
        return render(request, 'liste_project.html', {'username': username, 'projects': list_project})
    liste_dataset=projet['data_set']
    if request.method == 'POST':
        filename = request.POST.get('filename', None)
        action = request.POST.get('action', None)
        if action=="action" or action==None:
            if not filename:
                filename,columns,dico_info,table_html,df,dico_type,rows,columns=None,None,None,None,None,None,None,None
            else:
                table_html,df=df_to_html(username,filename,project_name)      
                dico_info=info_df(df)
                dico_type=colonne_type(df)
                rows = df.to_dict(orient='records')
                columns=df.columns
            return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                'filename':filename,'dico_info':dico_info,'table_html':table_html,'dico_type':dico_type,
                                                'df':df,'rows':rows,'columns':columns})
        elif action=="action1" :
            fs = gridfs.GridFS(db)
            grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
            if grid_out: 
                return redirect('process_dataset',project_name,filename,0)
            else:
                return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                        'filename':filename,})
        elif action=="action2":
            fs = gridfs.GridFS(db)
            grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
            if grid_out:
                file_data = BytesIO(grid_out.read())
                df = pd.read_csv(file_data,sep=',',on_bad_lines='warn')
                df = magic_clean(df)
                save_dataset(filename,project_name,username,df)
                dico_info=info_df(df)
                table_html,df=df_to_html(username,filename,project_name)      
                dico_type=colonne_type(df)
                rows = df.to_dict(orient='records')
                columns=df.columns
                return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                'filename':filename,'dico_info':dico_info,'table_html':table_html,'dico_type':dico_type,
                                                'df':df,'rows':rows,'columns':columns})
            else:
                return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                        'filename':filename,})
        elif action=="action3":
            print(filename)
            msg=delete_dataset(filename,username,project_name)
            projet=collection.find_one({'username':username,'nom_projet':project_name})
            liste_dataset=projet['data_set']
            return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset})
    else :
        return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset})

@login_required
def upload_csv(request,project_name):
    username=request.user.username
    db,client = get_db_mongo('Auto_ML','localhost',27017)
    collection = db['Projet']
    fs = gridfs.GridFS(db)

    if request.method == 'POST':
        print(request.FILES['csv_file'].name)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']           
            projet=collection.find_one({'username':username,'nom_projet':project_name})
            if projet:
                if not test_csv(username,csv_file.name,project_name):
                    file_id = fs.put(
                        csv_file, 
                        filename={'csv_file_name':csv_file.name,'username':username}, 
                        metadata={"username": username,'filename':csv_file.name,'project_name':project_name},
                        chunkSizeBytes=1048576
                    )
                    collection.update_one({'username':username,'nom_projet':project_name},{"$push": {"data_set": csv_file.name}})
        client.close()
        return redirect('project',project_name)
    else :
        client.close()
        form = UploadFileForm()
        
@login_required
def creer_project(request):
    username=request.user.username
    db,client = get_db_mongo('Auto_ML','localhost',27017)
    collection =db['Projet']
    collection2= db['User']
    if request.method == 'POST':
        nom_projet = request.POST.get("nom_projet")
        if nom_projet: 
            test_nom = collection.find_one({"nom_projet": nom_projet,"username":username})
            if test_nom:
                print('erreur_nom')
            else :
                ajout=collection.insert_one({"nom_projet": nom_projet, "username": request.user.username, 'id_user':request.user.id,'data_set':[]})
                project_id = ajout.inserted_id
                collection2.update_one({"username": request.user.username},{"$push": {"projet": project_id}})  
    return redirect('liste_project')

@login_required
def process_dataset(request, project_name, filename, a):
    methods, method_col, msg, liste_encod_cat,liste_encod_num= ['drop', 'mode', 'median', 'mean'], {'drop': 'columns', 'mode': 'numerical_columns', 'mean': 'numerical_columns', 'median': 'numerical_columns'},None,['One Hot','Label'],['Standard','Min-Max']
    username = request.user.username
    db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
    if a == 0:
        fs = gridfs.GridFS(db)
        grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename, 'metadata.project_name': project_name})
        file_data = BytesIO(grid_out.read())
        df = pd.read_csv(file_data, sep=',', on_bad_lines='warn')

        # Sauvegarde du DataFrame dans la session sous forme sérialisée
        request.session['df'] = df.to_dict()  # Convertit en dictionnaire

        categorical_columns, numerical_columns = type_column(df)
        columns, dico_type, rows = afficher_df(df)
    elif a == 1:
        # Récupère le DataFrame depuis la session
        df_dict = request.session.get('df', None)
        if df_dict is None:
            raise ValueError("Le DataFrame n'est pas disponible dans la session.")
        df = pd.DataFrame.from_dict(df_dict)

        categorical_columns, numerical_columns = type_column(df)
        columns, dico_type, rows = afficher_df(df)
    if request.method == 'POST':
        action = request.POST.get('action_process', None)
        if action == 'action1':
            col,method, text = request.POST.get('column', None), request.POST.get('method', None), request.POST.get('replace-text', None)
            df = valeurs_manquantes(df, col, method, text)
        if action == 'action2':
            df = df.drop_duplicates()
        if action == 'action3':
            col, old_value, new_value = request.POST.get('column', None), request.POST.get('text-to-replace', None), request.POST.get('replace-text2', None)
            df,msg = replace(df,col,old_value,new_value)
        if action == 'action4':
            col,encoding_method = request.POST.getlist('columns', None), request.POST.get('encoding_method', None)
            print(col, encoding_method)
            df, message = encode_categorical(df, col, encoding_method)
        if action == 'action5':
            col,encoding_method = request.POST.getlist('columns', None), request.POST.get('encoding_method', None)
            print(col, encoding_method)
            df,message=encode_numerical(df,col,encoding_method)

        # Mettez à jour le DataFrame dans la session
        request.session['df'] = df.to_dict()
        columns, dico_type, rows = afficher_df(df)
    a=1
    dico_info=info_df(df)
    return render(request, 'process_dataset.html', {'username': username,'project_name': project_name,'columns': columns,'methods': methods,
        'categorical_columns': categorical_columns,'numerical_columns': numerical_columns,'df': df,'dico_type': dico_type,'rows': rows,
        'filename': filename,'method_col': method_col,'a': a,"dico_info":dico_info,"message":msg,'encoding_methods_cat':liste_encod_cat,
        'encoding_methods_num':liste_encod_num})


def info_df(df):
    ligne = df.shape[0]
    colonne = df.shape[1]
    nb_nul = df.isnull().sum().to_frame().to_html()
    nb_colonne_double = df.duplicated().sum()
    return {'ligne':ligne,'colonne':colonne,
            'nb_nul':nb_nul,'nb_colonne_double':nb_colonne_double}

def df_to_html(username,filename,project_name):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
    if grid_out:
        file_data = BytesIO(grid_out.read())
        df = pd.read_csv(file_data,sep=',',on_bad_lines='warn')
        table_html=df.to_html(classes='display',table_id="dataframe-table",index=False)
    return table_html,df
        
def test_csv(username, filename,project_name):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    file = fs.find({"metadata.username": username,'metadata.filename':filename,'metadata.project_name':project_name})
    if len(list(file))==0:
        return None
    else:
        return 1
    
def get_project_by_user(username,id):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    collection =db['Projet']
    collection2= db['User']
    user_project = collection2.find_one({'username':username})
    liste=[]
    if user_project:
        for id in user_project['projet']:
            projet=collection.find_one({'_id':id})
            if projet:
                liste.append(projet)
    return liste

def get_file_csv_by_user(username):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    files = fs.find({"metadata.username": username})
    return files

def magic_clean(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.replace(r'[\s\x00-\x1F\x7F-\x9F]+', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='ignore')
        df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
        try :
            converted = pd.to_numeric(df[col], errors='raise')
            if converted.notna().all():
                try:
                    df[col]=df[col].astype(int)
                except:
                    df[col]=df[col].astype(float)
        except :
            test1=df[col].apply(lambda x: isinstance(x, dict)).all()
            test2=df[col].apply(lambda x: isinstance(x, list)).all()
            if test1==True or test2==True:
                pass
            else:
                df[col]=df[col].astype(str)
    return df

def type_column(df):
    df=magic_clean(df)
    categorical_column=df.select_dtypes(include=["category",'object']).columns.tolist()
    numerical_column=df.select_dtypes(include=['number']).columns.tolist()
    return categorical_column, numerical_column

def save_dataset(filename,project_name,username,df):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    file = fs.find_one({"metadata.username": username,"metadata.project_name":project_name,"metadata.filename":filename})
    if not file:
        return None
    else:
        metadata=file.metadata
        filename2=file.filename
        file_id=file._id
        fs.delete(file_id)
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        new_file_id = fs.put(csv_buffer.getvalue(), filename=filename2, metadata=metadata)
        return new_file_id

def colonne_type(df):
    return {
        col: type(df[col].iloc[0]).__name__ if len(df[col]) > 0 else 'NoneType'
        for col in df.columns
    }

def afficher_df(df):
    columns=df.columns   
    dico_type=colonne_type(df)
    rows = df.to_dict(orient='records')
    return columns,dico_type,rows

def delete_dataset(filename,username,project_name):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    collection = db['Projet']
    fs = gridfs.GridFS(db)
    file = fs.find_one({"metadata.username": username,"metadata.project_name":project_name,"metadata.filename":filename})
    if not file:
        return None
    else :
        file_id=file._id
        fs.delete(file_id)
        user_project=collection.find_one({"username":username,"nom_projet":project_name})
        dataset = user_project.get('data_set', [])
        dataset.remove(filename)
        collection.update_one({"username": username, "nom_projet": project_name},{"$set": {"data_set": dataset}})
    return {"success": True, "message": "Dataset supprimé avec succès."}

def delete_project(username,project_name):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    collection = db['Projet']
    fs = gridfs.GridFS(db)
    project = collection.find_one({"username": username,"nom_projet":project_name})
    if not project:
        return None
    else :
        files=project.get('data_set', [])
        if files :
            for filename in files:
                file = fs.find_one({"metadata.username": username,"metadata.project_name":project_name,"metadata.filename":filename})
                if not file:
                    pass
                else :
                    file_id=file._id
                    fs.delete(file_id)
        project_id=project.get('_id')
        collection.delete_one({'_id':project_id})
        return {"success": True, "message": "Projet supprimé avec succès."}

def valeurs_manquantes(df,col, missing_strategy,text=None):
    if missing_strategy == "mean":
        df[col].fillna(df[col].mean(), inplace=True)
    elif missing_strategy == "median":
        df[col].fillna(df[col].median(), inplace=True)
    elif missing_strategy == "mode":
        df[col].fillna(df[col].mode()[0], inplace=True)
    elif missing_strategy == "drop":
        df.dropna(subset=[col], inplace=True)
    elif missing_strategy == "replace":
        df[col].fillna(text, inplace=True)
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
    col2 =col.copy()
    for c in col2 :
        if c not in df.columns:
            col.remove(c)
    if len(col)>0:
        if encoding_method == "One Hot":
            encoder = OneHotEncoder(sparse_output=False, drop='first')
            encoded = encoder.fit_transform(df[col])
            encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(col))
            df = df.drop(columns=col).reset_index(drop=True)
            df = pd.concat([df, encoded_df], axis=1)

        elif encoding_method == "Label":
            for column in col:
                le = LabelEncoder()
                df[column] = le.fit_transform(df[column])

        else:
            return df, "Méthode d'encodage invalide. Utilisez 'onehot' ou 'label'."
    else :
        return df, "Colonne n'existe pas"

    return df , " tout c'est bien passé"

def encode_numerical(df,col,encoding_method):
    if isinstance(col, str):
        col = [col]
    col2 =col.copy()
    for c in col2 :
        if c not in df.columns:
            col.remove(c)
    if len(col)>0:
        if encoding_method == "Standard":
            scaler = StandardScaler() 
        elif encoding_method == "Min-Max":
            scaler = MinMaxScaler()
        else:
            return df, "Méthode d'encodage invalide. Utilisez 'onehot' ou 'label'."
        encoded = scaler.fit_transform(df[[col]])
        encoded_df = pd.DataFrame(encoded, columns=scaler.get_feature_names_out(col))
        df = df.drop(columns=col).reset_index(drop=True)
        df = pd.concat([df, encoded_df], axis=1)
    else :
        return df, "Colonne n'existe pas"
    return df ,'tout est bon'