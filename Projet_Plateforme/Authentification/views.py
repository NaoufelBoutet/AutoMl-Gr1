from django.shortcuts import render, redirect
from . import forms 
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse

# Vue pour gérer les inscriptions
def inscriptions(request):
    if request.method == 'POST':  # Si la méthode de la requête est POST (le formulaire a été soumis)
        form = forms.RegistrationForm(request.POST)  # Crée une instance du formulaire avec les données soumises
        print('POST ok')
        if form.is_valid():  # Si le formulaire est valide (tous les champs sont remplis correctement)
            print('FORMULAIRE ok')
            # On utilise commit=False pour créer l'objet sans l'enregistrer immédiatement dans la base de données
            user = form.save(commit=False)
            # Utilise set_password pour chiffrer le mot de passe au lieu de le stocker en clair
            user.set_password(form.cleaned_data['password'])
            user.save()  # Sauvegarde l'utilisateur dans la base de données
            login(request, user)  # Connecte l'utilisateur immédiatement après l'inscription
            return redirect('hello')  # Redirige vers la page d'accueil après l'inscription réussie
    else:
        form = forms.RegistrationForm()  # Si la méthode est GET, on crée un formulaire vierge
    return render(request, 'inscriptions.html', {'form': form})  # Affiche le formulaire dans le template

def login_view(request): # Définition de la vue de connexion qui prend un objet request comme argument
    if request.method == 'POST': # Vérifie si la requête est de type POST, ce qui signifie que l'utilisateur a soumis le formulaire de connexion
        form = AuthenticationForm(request, data=request.POST) # Instancie un formulaire d'authentification Django avec les données POST envoyées par l'utilisateur
        if form.is_valid(): # Vérifie si les données soumises dans le formulaire sont valides (si les champs sont correctement remplis)
            username = form.cleaned_data.get('username')# Récupère le nom d'utilisateur après validation et nettoyage des données
            password = form.cleaned_data.get('password') # Récupère le mot de passe après validation et nettoyage des données
            user = authenticate(username=username, password=password) # Tente d'authentifier l'utilisateur avec le nom d'utilisateur et le mot de passe fournis
            if user is not None: # Si l'authentification réussit (l'utilisateur existe et le mot de passe est correct)
                login(request, user) # Connecte l'utilisateur à la session active
                return redirect('hello')  # Redirige vers la page d'accueil "hello" après connexion
            else:
                return HttpResponse("Invalid username or password.")  # Si l'authentification échoue (nom d'utilisateur ou mot de passe incorrect), renvoie un message d'erreur
    else:
        form = AuthenticationForm() # Si la requête n'est pas de type POST, crée un formulaire d'authentification vide pour être affiché
    return render(request, 'login.html', {'form': form}) # Affiche la page 'login.html' avec le formulaire d'authentification pour que l'utilisateur puisse le remplir
