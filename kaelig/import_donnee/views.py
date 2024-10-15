from django.shortcuts import render
import csv
from utils import get_db_mongo
import pymongo
import gridfs

def home_import_data(request):
    return render(request, 'home_import_data.html')

def test_csv(username,filename):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    fs = gridfs.GridFS(db)
    file = fs.find({"metadata.username": username,'metadata.filename':filename})
    if file.count()==0:
        return None
    else:
        return 1

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
