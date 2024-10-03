from django.http import HttpResponse
from django.shortcuts import render
from Exploration_donnees.models import Utilisateurs


def hello(request):
    utilisateurs = Utilisateurs.objects.all()
    return render(request, 'Exploration_donnees/hello.html',
        {'utilisateurs': utilisateurs})

