from django.shortcuts import render, redirect
from . import forms # Assurez-vous d'importer le bon formulaire depuis votre fichier forms.py
from django.contrib.auth import login

# Vue pour gérer les inscriptions
def inscriptions(request):
    if request.method == 'POST':  # Si la méthode de la requête est POST (le formulaire a été soumis)
        form = forms.RegistrationForm(request.POST)  # Créer une instance du formulaire avec les données soumises
        if form.is_valid():  # Si le formulaire est valide (tous les champs sont remplis correctement)
            # On utilise commit=False pour créer l'objet sans l'enregistrer immédiatement dans la base de données
            user = form.save(commit=False)
            # Utiliser set_password pour chiffrer le mot de passe au lieu de le stocker en clair
            user.set_password(form.cleaned_data['password'])
            user.save()  # Sauvegarder l'utilisateur dans la base de données
            
            login(request, user)  # Connecter l'utilisateur immédiatement après l'inscription
            return redirect('Exploration_donnees/hello')  # Rediriger vers la page d'accueil après l'inscription réussie
    else:
        form = forms.RegistrationForm()  # Si la méthode est GET, on crée un formulaire vierge

    return render(request, 'inscriptions.html', {'form': form})  # Afficher le formulaire dans le template

