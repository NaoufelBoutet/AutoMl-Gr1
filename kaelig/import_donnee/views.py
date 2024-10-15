from django.shortcuts import render
import csv
from utils import get_db_mongo
import pymongo
import gridfs

def home_data(request,username):
    return render(request, 'home_data.html',{'username' : username})

def test_csv(username, filename):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    file = fs.find({"metadata.username": username,'metadata.filename':filename})
    if file.count()==0:
        return None
    else:
        return 1

def import_csv(request, username):
    db,client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)

    if request.method == 'POST' and request.FILES['csv_file']:
        # Récupérer le fichier téléversé
        csv_file = request.FILES['csv_file']

        # S'assurer que c'est bien un fichier CSV
        if not csv_file.name.endswith('.csv'):
            return render(request, 'result.html', {'message': 'Ce fichier n\'est pas un CSV'})

        if not test_csv(username,csv_file.name):
            file_id = fs.put(
                csv_file, 
                filename=csv_file.name, 
                metadata={"username": username,'filename':csv_file.name}
            )

        else:
            return render(request, 'result.html', { 'message': 'le fichier existe deja'})
    client.close()
    return render(request, 'result.html', { 'message': 'le fichier est bien enregistrer'})
        








# Create your views here.
