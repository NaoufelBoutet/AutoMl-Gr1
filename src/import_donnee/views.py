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

@login_required
def home_data(request):
    username=request.user.username
    return render(request, 'home_data.html',{'username' : username})

@login_required
def liste_project(request):
    username=request.user.username
    id=request.user.id
    list_project=get_project_by_user(username,id)
    print(list_project)
    return render(request, 'liste_project.html',{'username' : username,'projects' : list_project})

@login_required
def project(request,project_name):
    username=request.user.username
    filename = request.GET.get('filename', None)
    action = request.GET.get('action', None)
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    collection = db['Projet']
    projet=collection.find_one({'username':username,'nom_projet':project_name})
    liste_dataset=projet['data_set']
    print(action)
    if action=="action" or action==None:
        if not filename:
            filename=None
            dico_info=None
            table_html=None
        else:
            dico_info=read_csv(username,project_name,filename)
            table_html,df=df_to_html(username,filename,project_name)        
        return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                            'filename':filename,'dico_info':dico_info,'table_html':table_html})
    else :
        fs = gridfs.GridFS(db)
        grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
        if grid_out:
            file_data = BytesIO(grid_out.read())
            df = pd.read_csv(file_data,sep=',',on_bad_lines='warn')
            categorical_columns, numerical_columns = type_column(df)
            return render(request,'process_dataset.html',{'project_name':project_name,'filename':filename,'username':username,
                                                      'categorical_columns':categorical_columns,'numerical_columns':numerical_columns})
        else:
            return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                    'filename':filename,})
    
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
                    return redirect('project',project_name,None)
                else:
                    return redirect('project',project_name,None)
            else:
                client.close()
                return redirect('project',project_name,None)
        else:
            client.close()
            return redirect('project',project_name,None)
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
            print(nom_projet)
            test_nom = collection.find_one({"nom_projet": nom_projet,"username":username})
            if test_nom:
                print('erreur_nom')
            else :
                ajout=collection.insert_one({"nom_projet": nom_projet, "username": request.user.username, 'id_user':request.user.id,'data_set':[]})
                project_id = ajout.inserted_id
                collection2.update_one({"username": request.user.username},{"$push": {"projet": project_id}})
                print('doc enregistré')  
    return redirect('liste_project')

@login_required
def process_dataset(request,project_name):
    username=request.user.username
    filename = request.GET.get('filename', None)
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
    if grid_out:
        print('okkkk')
        file_data = BytesIO(grid_out.read())
        df = pd.read_csv(file_data,sep=',',on_bad_lines='warn')
        categorical_columns, numerical_columns = type_column(df)
    return render(request, 'process_dataset.html', {'username':username,'project_name':project_name,
                                                    'categorical_columns':categorical_columns,'numerical_columns':numerical_columns})

def read_csv(username, project_name, filename):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
    print(username,filename,project_name)
    if grid_out:
        file_data = BytesIO(grid_out.read())
        df = pd.read_csv(file_data,sep=',',on_bad_lines='warn')
        ligne = df.shape[0]
        colonne = df.shape[1]
        nb_nul = df.isnull().sum().to_frame().to_html()
        nb_colonne_double = df.duplicated().sum()
        return {'username':username,'ligne':ligne,'colonne':colonne,
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

def remove_invisible_chars(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.replace(r'[\s\x00-\x1F\x7F-\x9F]+', '', regex=True)
    return df

def identify_column_type(df):
    numeric_like = []
    categorical_like = []
    df=remove_invisible_chars(df)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
        try:
            df[col] = df[col].str.replace(',', '.', regex=False)
            converted = pd.to_numeric(df[col], errors='coerce')
            if converted.notna().all():
                numeric_like.append(col)
            else:
                categorical_like.append(col)
        except Exception:
            categorical_like.append(col)
    return numeric_like, categorical_like

def type_column(df):
    categorical_column=df.select_dtypes(include=["category"]).columns.tolist()
    numerical_column=df.select_dtypes(include=['number']).columns.tolist()
    num, cat = identify_column_type(df)
    categorical_column+=cat
    numerical_column+=num
    print(f"num:{numerical_column},cat:{categorical_column}")
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
        print(file_id)
        fs.delete(file_id)
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        new_file_id = fs.put(csv_buffer.getvalue(), filename=filename2, metadata=metadata)
        print(new_file_id)
        return new_file_id
