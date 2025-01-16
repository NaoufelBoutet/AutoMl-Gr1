from django.shortcuts import render
from utils import get_db_mongo
from django.contrib.auth.decorators import login_required

def create_collections():
    db, client = get_db_mongo('Auto_ML','localhost',27017)
    if "User" not in db.list_collection_names():
        db.create_collection("User")
    if "Projet" not in db.list_collection_names():
        db.create_collection("Projet")
    client.close()

def home(request):
    return render(request, 'accueil.html')

@login_required
def espace_personel(request):
    username=request.user.username
    return render(request, 'espace_perso.html',{'username': username})

