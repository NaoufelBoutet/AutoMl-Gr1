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

@login_required
def df_to_html(request, filename,project_name):
    username=request.user.username
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename})
    if grid_out:
        file_data = BytesIO(grid_out.read())
        df = pd.read_csv(file_data,sep=',',on_bad_lines='warn')
        table_html=df.to_html(classes='display',table_id="dataframe-table",index=False)
    return render(request, 'df_html.html', {'username':username,'table_html': table_html,'file_choisi':filename,'project_name':project_name})

@login_required
def project(request,project_name,filename):
    username=request.user.username
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    collection = db['Projet']
    projet=collection.find_one({'username':username,'nom_projet':project_name})
    liste_dataset=projet['data_set']
    if filename=='None':
        filename=None
    else:
        dico_info=read_csv(username,project_name,filename)
    return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,'filename':filename,'dico_info':dico_info})

        
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
                else:
                    return redirect('project',project_name)
            else:
                client.close()
                return redirect('project',project_name)
        else:
            client.close()
            return redirect('project',project_name)
    else :
        client.close()
        form = UploadFileForm()

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



# Create your views here.
