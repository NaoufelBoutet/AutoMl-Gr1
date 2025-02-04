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
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder,MinMaxScaler,RobustScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import matplotlib
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import warnings
import random
from django.http import JsonResponse
from celery.result import AsyncResult
from .tasks import train_model_task
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


matplotlib.use('Agg')

@login_required
def home_data(request):
    username=request.user.username
    task_id = request.session.get("task_id", None)
    return render(request, 'home_data.html',{'username' : username,"task_id": task_id})

@login_required
def liste_project(request):
    username = request.user.username
    id = request.user.id   
    list_project = get_project_by_user(username, id)  
    print("1:",list_project)
    task_id = request.session.get("task_id", None)
    if request.method == 'POST':
        action = request.POST.get('action_liste_prj', None)
        projet = request.POST.get('projet', None)
        if action == 'action1':
            delete_project(username, projet)  
            list_project = get_project_by_user(username, id)  
            print("2",list_project)
    return render(request, 'liste_project.html', {'username': username, 'projects': list_project,"task_id": task_id})

@login_required
def project(request,project_name):
    username=request.user.username
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    collection = db['Projet']
    projet=collection.find_one({'username':username,'nom_projet':project_name})
    task_id = request.session.get("task_id", None)
    if not projet :
        id = request.user.id   
        list_project = get_project_by_user(username, id) 
        return render(request, 'liste_project.html', {'username': username, 'projects': list_project,"task_id": task_id})
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
                                                'df':df,'rows':rows,'columns':columns,"task_id": task_id})
        elif action=="action1" :
            fs = gridfs.GridFS(db)
            grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
            if grid_out: 
                try:
                    del request.session['df']
                except:
                    pass
                return redirect('process_dataset',project_name,filename)
            else:
                return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                        'filename':filename,"task_id": task_id})
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
                                                'df':df,'rows':rows,'columns':columns,"task_id": task_id})
            else:
                return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                        'filename':filename,"task_id": task_id})
        elif action=="action3":
            print(filename)
            msg=delete_dataset(filename,username,project_name)
            projet=collection.find_one({'username':username,'nom_projet':project_name})
            liste_dataset=projet['data_set']
            return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,"task_id": task_id})
        elif action=="action4":
            fs = gridfs.GridFS(db)
            grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
            if grid_out: 
                try:
                    del request.session['df']
                except:
                    pass
                return redirect('viz_data',project_name,filename)
            else:
                return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                        'filename':filename,"task_id": task_id})
        elif action=="action5":
            fs = gridfs.GridFS(db)
            grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename,'metadata.project_name':project_name})
            if grid_out: 
                try:
                    del request.session['target']
                    del request.session['features']
                except:
                    pass
                return redirect('ML',project_name,filename)
            else:
                return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,
                                                        'filename':filename,"task_id": task_id})

    else :
        return render(request,'project.html',{'username':username,'project_name':project_name,'liste_dataset':liste_dataset,"task_id": task_id})

@login_required
def upload_csv(request,project_name):
    task_id = request.session.get("task_id", None)
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
                ajout=collection.insert_one({"nom_projet": nom_projet, "username": request.user.username, 'id_user':request.user.id,'data_set':[],'graphique':[]})
                project_id = ajout.inserted_id
                collection2.update_one({"username": request.user.username},{"$push": {"projet": project_id}})  
    return redirect('liste_project')

@login_required
def process_dataset(request, project_name, filename):
    task_id = request.session.get("task_id", None)
    methods, method_col, msg, liste_encod_cat,liste_encod_num= ['drop', 'mode', 'median', 'mean'], {'drop': 'columns', 'mode': 'numerical_columns', 'mean': 'numerical_columns', 'median': 'numerical_columns'},None,['One Hot','Label'],['Standard','Min-Max','Robust']
    username = request.user.username
    db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
    df_dict = request.session.get('df', None) 
    outliers,columns_out, dico_type_out, rows_out=None,None,None,None
    if df_dict is None:
        # Si le DataFrame n'est pas dans la session, le charger depuis GridFS
        fs = gridfs.GridFS(db)  # Assurez-vous que 'settings.DB' pointe vers votre base de données MongoDB
        grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename, 'metadata.project_name': project_name}) 
        if grid_out:
            file_data = BytesIO(grid_out.read())
            df = pd.read_csv(file_data, sep=',', on_bad_lines='warn')
            request.session['df'] = df.to_dict()  # Convertit en dictionnaire   
        else:
            # Gestion du cas où le fichier n'est pas trouvé
            return "Fichier non trouvé dans GridFS"
    else:
        # Si le DataFrame est déjà dans la session, le reconstruire à partir du dictionnaire
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
            df, message = encode_categorical(df, col, encoding_method)
        if action == 'action5':
            col,encoding_method = request.POST.getlist('columns', None), request.POST.get('encoding_method', None)
            df,message=encode_numerical(df,col,encoding_method)
        if action == 'action6':
            col = request.POST.getlist('columns', None)
            outliers = func_outliers(df[numerical_columns],col)
            df_outliers = df.loc[outliers]    
            columns_out, dico_type_out, rows_out = afficher_df(df_outliers)
        if action == 'del_outlier':
            selected_rows = request.POST.getlist('selected_rows')
            if 'all' in selected_rows:
                selected_rows = request.POST.get('index_all', '').split(',')
            else:
                selected_rows = request.POST.getlist('selected_rows')
            for element in selected_rows:
                try:
                    df=df.drop(index=element)
                    message = 'Nickel'
                except Exception as e:
                    message = f'Erreur lors de la suppression de la ligne: {e}'
                    pass      
        if action == 'save_df':
            response=save_dataset(filename,project_name,username,df)
        # Mettez à jour le DataFrame dans la session
        request.session['df'] = df.to_dict()
        columns, dico_type, rows = afficher_df(df)
    a=1
    dico_info=info_df(df)
    return render(request, 'process_dataset.html', {'username': username,'project_name': project_name,'columns': columns,'methods': methods,
        'categorical_columns': categorical_columns,'numerical_columns': numerical_columns,'df': df,'dico_type': dico_type,'rows': rows,
        'filename': filename,'method_col': method_col,'a': a,"dico_info":dico_info,"message":msg,'encoding_methods_cat':liste_encod_cat,
        'encoding_methods_num':liste_encod_num,'outliers':outliers,'columns_out':columns_out, 'dico_type_out':dico_type_out, 'rows_out':rows_out,
        "task_id": task_id})

@login_required
def viz_data(request, project_name, filename):
    task_id = request.session.get("task_id", None)
    methods, message= ['Boxplot','Histogramme'], None 
    username = request.user.username
    db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
    fs = gridfs.GridFS(db)
    grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename, 'metadata.project_name': project_name})
    file_data = BytesIO(grid_out.read())
    df = pd.read_csv(file_data, sep=',', on_bad_lines='warn')
    categorical_columns, numerical_columns = type_column(df)
    figs = request.session.get('figs', None) 
    figs_bdd = request.session.get('figs_bdd', None) 
    liste_graph_name, dic_graph = liste_graph(db, username, project_name)
    if figs is None:
        figs=[]   
    if figs_bdd is None:
        figs_bdd=[]
    if request.method == 'POST':
        action = request.POST.get('action_process', None)
        if action=='action0':
            graph=request.POST.get('graph', None)
            figs.append(dic_graph[graph])
            figs_bdd.append(dic_graph[graph])
            liste_graph_name, dic_graph = liste_graph(db, username, project_name)
        if action=='action1':
            col, method = request.POST.getlist('columns', None),request.POST.get('method', None)
            if 'all' in col:
                col=numerical_columns
            if col==[]:
                message = "selectionner une colonne"
            elif method!=None:
                figs.append(plot_1D(df,col,method))

        if action == 'action2':
            col1 = request.POST.get('column1', None)
            col2 = request.POST.get('column2', None)
            figs.append(scatterplot(col1,col2,df))
        
        if action == 'action3':
            figs.append(matrix_corr(df[numerical_columns]))

        if action == 'save':
            name = request.POST.get('graph_name', None)
            fig_save = request.POST.get('fig_data',None)
            graph_name = filename + "__" + name
            message = save_graph(graph_name,project_name,username,figs[int(fig_save)])
            figs_bdd.append(figs[int(fig_save)])
            liste_graph_name, dic_graph = liste_graph(db, username, project_name)
        if action =='del':
            fig_del = request.POST.get('fig',None)
            try:
                figs.remove(fig_del)
                message = " Graph retiré "
                print(message)
            except:
                pass
        if action =='del_bdd':
            fig_del,fig_del2, filename_del = request.POST.get('fig_data',None),request.POST.get('fig',None),request.POST.get('graph_key_value',None)
            try:
                figs.remove(fig_del2)
                figs_bdd.remove(fig_del2)
            except:
                pass
            msg = delete_graph(filename_del,username,project_name)
            message=msg['message']
            liste_graph_name, dic_graph = liste_graph(db, username, project_name)

        request.session['figs'] = figs
        request.session['figs_bdd']=figs_bdd
    return render(request,'viz_data.html',{'username': username,'project_name': project_name,'filename': filename,'methods':methods,
                                           'numerical_columns':numerical_columns, 'figs':figs, 'message':message,"task_id": task_id,
                                           'liste_graph_name' : liste_graph_name,'figs_bdd':figs_bdd,'dic_graph':dic_graph})

@login_required
def ML(request, project_name, filename):
    task_id = request.session.get("task_id", None)
    username = request.user.username
    db, client = get_db_mongo('Auto_ML', 'localhost', 27017)
    fs = gridfs.GridFS(db)
    grid_out = fs.find_one({"metadata.username": username, 'metadata.filename': filename, 'metadata.project_name': project_name})
    file_data = BytesIO(grid_out.read())
    df = pd.read_csv(file_data, sep=',', on_bad_lines='warn')
    columns, dico_type, rows = afficher_df(df)
    target = request.session.get('target', None) 
    features = request.session.get('features', None)   
    if request.method == 'POST':
        action = request.POST.get('action_process', None)
        if action=='target_features':
            target = request.POST.get('target', None)
            features = request.POST.getlist('features',None)
            if target in features:
                features.remove(str(target))
            if 'all' in features:
                features = columns.tolist().copy()
                features.remove(target)
        if action == 'machine_learning':
            if target is not None and features is not None and features!=[]:
                if target not in features:
                    features.append(target)
                df = df[features]
                X_train,X_test,Y_train, Y_test = split_data(df, target)
                task = train_model_task.apply_async(args=[X_train.values.tolist(), Y_train.values.tolist()])

                request.session['task_id'] = task.id
                return redirect('ML',project_name, filename)
                
        request.session['target']=target
        request.session['features']=features
    return render(request,'ML.html',{'username': username,'project_name': project_name,'filename': filename,'columns':columns,'target':target,
                                     'features':features,"task_id": task_id})

def get_task_progress(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        "state": result.state,
        "meta": result.info if result.info else {}
    }
    return JsonResponse(response_data)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def clear_task_id(request):
    if request.method == "POST":
        request.session.pop("task_id", None)  # Supprime task_id de la session
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)
        

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

def save_graph(filename,project_name,username,file):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    test_file = fs.find_one({"metadata.username": username,"metadata.project_name":project_name,"metadata.filename":filename})
    collection=db['Projet']
    if not test_file:
        try:
            file_binary = base64.b64decode(file)
            file = io.BytesIO(file_binary) 
        except Exception as e:
            file = io.StringIO(file)
        file_id = fs.put(file, filename={'graph_file_name':filename,'username':username}, 
                            metadata={"username": username,'filename':filename,'project_name':project_name},
                            chunkSizeBytes=1048576
                        )
        collection.update_one({'username':username,'nom_projet':project_name},{"$push": {"graphique": filename}})
        return 'graphique sauvegarder'
    else:
        return 'graphique deja existant'
    
def liste_graph(db, username, project_name):
    fs = gridfs.GridFS(db)
    collection = db['Projet']
    projet = collection.find_one({'username': username, 'nom_projet': project_name})
    if not projet or 'graphique' not in projet:
        return [], []     
    graphs= projet['graphique']
    liste_graph_name, dic_graph = [], {}
    
    for filename in graphs:
        graph = fs.find_one({"metadata.username": username,"metadata.project_name":project_name,"metadata.filename":filename})
        if graph:  
            graph_file_name = graph.metadata.get('filename') if graph.metadata else None
            liste_graph_name.append(graph_file_name)
            dic_graph[graph_file_name]=base64.b64encode(graph.read()).decode('utf-8')
    return liste_graph_name, dic_graph


def colonne_type(df):
    return {
        col: type(df[col].iloc[0]).__name__ if len(df[col]) > 0 else 'NoneType'
        for col in df.columns
    }

def afficher_df(df):
    columns=df.columns   
    dico_type=colonne_type(df)
    rows = df.reset_index().to_dict(orient='records')
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

def delete_graph(filename,username,project_name):
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
        graph = user_project.get('graphique', [])
        graph.remove(filename)
        collection.update_one({"username": username, "nom_projet": project_name},{"$set": {"graphique": graph}})
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
    magic_clean(df)
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
    magic_clean(df)
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
        elif encoding_method == "Robust":
            scaler = RobustScaler()
        else:
            return df, "Méthode d'encodage invalide. Utilisez 'onehot' ou 'label'."
        encoded = scaler.fit_transform(df[col])
        encoded_df = pd.DataFrame(encoded, columns=scaler.get_feature_names_out(col))
        df = df.drop(columns=col).reset_index(drop=True)
        df = pd.concat([df, encoded_df], axis=1)
    else :
        return df, "Colonne n'existe pas"
    return df ,'tout est bon'

def boxplot(df):
    # Créer le boxplot
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.boxplot(df.values, tick_labels=df.columns, vert=True)
    ax.set_xlabel("Valeurs")
    ax.set_ylabel("Colonnes")
    plt.grid()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  # Revenir au début du fichier binaire

    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Fermer le graphique pour libérer de la mémoire
    plt.close()

    return img_base64

def histplot(df):
    # Créer l'histogramme
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.hist(df.values, bins=5)
    ax.set_xlabel("Valeurs")
    ax.set_ylabel("Colonnes")
    plt.grid()
    # Sauvegarder l'image dans un buffer mémoire
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  # Revenir au début du fichier binaire
    # Convertir l'image en base64 pour l'afficher dans le HTML
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    # Fermer le graphique pour libérer de la mémoire
    plt.close()

    return img_base64

def plot_1D(df, col, method):
    df = df[col] 
    if method == 'Boxplot':
        img_base64 = boxplot(df)
    elif method == 'Histogramme':
        img_base64 = histplot(df)
    else:
        img_base64 = None  
    return img_base64

def scatterplot(colonne_x,colonne_y,df):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x=df[colonne_x], y=df[colonne_y], alpha=1, edgecolors='w',c='red')
    ax.set_xlabel(colonne_x)
    ax.set_ylabel(colonne_y)
    ax.set_title(f"Scatterplot de {colonne_x} vs {colonne_y}")
    plt.grid()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    return img_base64

def matrix_corr(df):
    fig=plt.figure(figsize=(16, 6))
    heatmap = sns.heatmap(df.corr(), vmin=-1, vmax=1, annot=True, cmap='BrBG')
    heatmap.set_title('Correlation Heatmap', fontdict={'fontsize':18}, pad=12)
    plt.grid()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    return img_base64

def func_outliers(df, colonne):
    Q1 = df[colonne].quantile(0.25)
    Q3 = df[colonne].quantile(0.75)
    IQR = Q3 - Q1
    
    outliers=df[(df[colonne] < (Q1 - 1.5 * IQR)) | (df[colonne] > (Q3 + 1.5 * IQR))]
    outliers_index=outliers.dropna(subset=colonne).index.tolist()
    print(outliers_index)
    return outliers_index

def train_model(X_train, y_train, model_name="random_forest", params=None, use_grid_search=False, search_models=False, scoring="accuracy", cv=5):
    """
    Entraîne un modèle de Machine Learning avec ou sans GridSearch, en gérant les erreurs potentielles.

    :param X_train: Features d'entraînement
    :param y_train: Labels d'entraînement
    :param model_name: Nom du modèle à utiliser (si search_models=False)
    :param params: Dictionnaire des paramètres si non None et use_grid_search=False
    :param use_grid_search: Si True, utilise GridSearch pour chercher les meilleurs hyperparamètres
    :param search_models: Si True, GridSearch explore aussi plusieurs modèles
    :param scoring: Métrique de scoring pour GridSearch (ex: "accuracy", "f1", "roc_auc", etc.)
    :param cv: Nombre de folds pour la validation croisée
    :return: Modèle entraîné et (si applicable) les meilleurs paramètres trouvés
    """

    models = {
        "random_forest": RandomForestClassifier(),
        "svm": SVC(),
        "logistic_regression": LogisticRegression()
    }
    param_grid = {
        "random_forest": {"n_estimators": [10, 50, 100], "max_depth": [None, 10, 20]},
        "svm": {"C": [0.1, 1, 10], "kernel": ["linear", "rbf"]},
        "logistic_regression": {"C": [0.1, 1, 10], "solver": ["liblinear"]}
    }

    # Pour stocker le meilleur modèle en cas de GridSearch sur plusieurs modèles
    best_model = None
    best_score = float('-inf')
    best_params = None
    models_tested = 0  # Compteur des modèles testés avec succès

    # Désactiver les warnings inutiles
    warnings.filterwarnings("ignore")
    if search_models:
            for model_key, model in models.items():
                try:
                    print(f"🔍 Optimisation du modèle: {model_key} avec scoring={scoring} et cv={cv}")
                    grid_search = GridSearchCV(model, param_grid[model_key], cv=cv, scoring=scoring)
                    grid_search.fit(X_train, y_train)

                    models_tested += 1  # Incrémenter si le modèle a fonctionné

                    if grid_search.bestscore > best_score:
                        best_score = grid_search.bestscore
                        best_model = grid_search.bestestimator
                        best_params = grid_search.bestparams

                except Exception as e:
                    print(f"⚠️ Erreur avec le modèle {model_key}: {e}")

            if best_model is None:
                print("❌ Aucun modèle n'a réussi à s'entraîner.")
            else:
                print(f"✅ Meilleur modèle trouvé: {best_model} avec score={best_score}")

            return best_model, best_params

    else:
        model = models.get(model_name)

        if model is None:
            print(f"❌ Modèle '{model_name}' non reconnu. Choisissez parmi {list(models.keys())}.")
            return None, None

        try:
            if use_grid_search:
                print(f"🔍 Recherche des meilleurs paramètres pour {model_name}...")
                grid_search = GridSearchCV(model, param_grid[model_name], cv=cv, scoring=scoring)
                grid_search.fit(X_train, y_train)
                return grid_search.bestestimator, grid_search.bestparams

            elif params:
                model.set_params(**params)

            print(f"🚀 Entraînement du modèle {model_name}...")
            model.fit(X_train, y_train)
            return model, params

        except Exception as e:
            print(f"⚠️ Erreur avec {model_name}: {e}")

        return None, None

def split_data(df, target_column, test_size=0.2, random_state=random.randint(10**4, 10**6 - 1)):
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)