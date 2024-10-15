from django.shortcuts import render
def home(request):
    return render(request, 'accueil.html')

def espace_personel(request,username:str):
    print('noooooooooooooooooooooooooooooooon')
    return render(request, 'espace_perso.html',{'username': username})

# Create your views here.
