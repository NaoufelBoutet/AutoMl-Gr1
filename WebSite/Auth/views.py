from django.shortcuts import render

# Create your views here.

def connexion(request):
    return render(request,"connexion.html")

def inscription(request):
    return render(request,"inscription.html")