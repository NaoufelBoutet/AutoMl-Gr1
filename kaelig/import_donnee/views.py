from django.shortcuts import render
import csv
from kaelig.utils import get_db_mongo

def import_csv(username,name,delimiter,quotechar):
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    collection = db['fichier_import']
    with open('eggs.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)






# Create your views here.
