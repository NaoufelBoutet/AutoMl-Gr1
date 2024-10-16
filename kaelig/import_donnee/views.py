from django.shortcuts import render, redirect
import csv
from utils import get_db_mongo
import pymongo
import gridfs
from .forms import UploadFileForm
from django.urls import reverse

def home_data(request,username):
    return render(request, 'home_data.html',{'username' : username})

def result_csv(request,username):
    message = request.GET.get('message', 'Aucun message fourni')
    return render(request, 'result.html',{'message' : message,'username' : username})

def test_csv(username, filename):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    file = fs.find({"metadata.username": username,'metadata.filename':filename})
    if len(list(file))==0:
        return None
    else:
        return 1

def upload_csv(request, username):
    db,client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)

    if request.method == 'POST':
        print(request.FILES['csv_file'].name)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            if not test_csv(username,csv_file.name):
                file_id = fs.put(
                    csv_file, 
                    filename={'csv_file_name':csv_file.name,'username':username}, 
                    metadata={"username": username,'filename':csv_file.name},
                    chunkSizeBytes=1048576
                )
                client.close()
                return redirect(reverse('result_csv', kwargs={'username': username}) + f"?message=Le fichier est bien enregistré")
            else:
                client.close()
                return redirect(reverse('result_csv', kwargs={'username': username}) + f"?message=Le fichier existe déjà")
        else:
            client.close()
            return render(request, 'home_data.html', {'form': form, 'username': username})
    else :
        client.close()
        form = UploadFileForm()


# Create your views here.
