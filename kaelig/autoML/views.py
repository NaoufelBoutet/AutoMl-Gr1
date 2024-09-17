from django.shortcuts import render
def home(request):
    return render(request, 'accueil.html')

def espace_personel(request,username:str):
    return render(request, 'espace_personel.html',{'username': username})

# Create your views here.
