from django.shortcuts import render
def home(request):
    return render(request, 'accueil.html')

def login(request):
    return render(request, 'login.html')

def sign(request): 
    return render(request, 'sign.html')
# Create your views here.
