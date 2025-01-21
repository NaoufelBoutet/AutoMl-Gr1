# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from utils import get_db_mongo
# from django.contrib import messages
# from .forms import UserForm
# from django.http import HttpResponse
# from django.contrib.auth import authenticate,login as auth_login
# import sqlite3

# conn = sqlite3.connect(r'C:\Users\naouf\Documents\1-Naoufel\1-projet\10-AutoMl\AutoMl-Gr1\src\db.sqlite3',check_same_thread=False)  # Remplacez par le chemin de votre base SQLite
# cursor = conn.cursor()

# def show_login(request):
#     return render(request, 'login.html')

# def show_sign(request): 
#     return render(request, 'sign.html')

# def sign_in(request):
#     if request.method=='POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']

#             if User.objects.filter(username=username).exists():
#                 messages.error(request, "Ce nom d'utilisateur est déjà pris.")
#             else:
#                 user = User.objects.create_user(username=username, password=password)
#                 user.save()
#                 messages.success(request, "Utilisateur créé avec succès.")
#                 cursor.execute("SELECT id FROM auth_user WHERE username = ?", (username,))
#                 resultat = cursor.fetchone()
#                 user_id = resultat[0]
                
#                 return redirect('show_login')
#         else:
#             return HttpResponse("Hello, World!")
#     return render(request, 'sign.html', {'form': form})

# def login(request):
#     if request.method=='POST':
#         form=UserForm(request.POST)
#         print(form)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user=authenticate(username=username,password=password)
#             if user is not None:
#                 auth_login(request, user)
#                 messages.success(request, "Utilisateur créé avec succès.")
#                 return redirect('perso', username=username)
#             else:
#                 messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
#                 return HttpResponse("Hello, World!")
#     return render(request, 'login.html', {'form': form})

# def success(request):
#     return render(request, 'sucess.html')

from django.shortcuts import render, redirect
from .form import ConnexionForm,InscriptionForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
# Create your views here.


def connexion(request):
    form = ConnexionForm()
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accueil')
            else:
                form.add_error(None, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, "connexion.html", {"form": form})

def deconnexion(request):
    logout(request)
    return redirect(connexion)

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  
            return redirect('accueil')  
    else:
        form = InscriptionForm()

    return render(request, 'inscription.html', {'form': form})
    


    

