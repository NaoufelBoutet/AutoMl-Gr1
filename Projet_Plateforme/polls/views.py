from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def contact_us(request):
    return HttpResponse(" Voici un formulaire de contact.")

def about_us(request):
    return HttpResponse('<h1>À propos de nous </h1> <p>Nous adorons les graphs, les statistiques et les modeles</p>')

def help(request):
    return HttpResponse(" Aide et Exemples.")