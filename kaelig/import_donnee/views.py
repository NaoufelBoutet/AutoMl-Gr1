from django.shortcuts import render
import csv
from utils import get_db_mongo
import pymongo
import gridfs

def home_data(request):
    return render(request, 'home_data.html')

def test_csv(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        # Récupérer le fichier téléversé
        csv_file = request.FILES['csv_file']

        # S'assurer que c'est bien un fichier CSV
        if not csv_file.name.endswith('.csv'):
            return render(request, 'import_donnee/home_data.html', {'error': 'Ce fichier n\'est pas un CSV'})


def import_csv(username,name,delimiter,quotechar):
    db,client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    filename=f"{name}.csv"
    if not test_csv(username,filename):
        with open("large_file.csv", "rb") as file:
            file_id = fs.put(
                file, 
                filename=filename, 
                metadata={"username": username,'filename':filename}
            )
    else:
        return 'le fichier existe deja'

        








# Create your views here.
