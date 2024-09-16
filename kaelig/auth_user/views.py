from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserForm

def show_login(request):
    return render(request, 'login.html')

def show_sign(request): 
    return render(request, 'sign.html')

def sign_in(request):
    if request.method=='POST':
        form = UserForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=UserForm.username).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            else:
                # Créer l'utilisateur
                user = User.objects.create_user(username=UserForm.username, password=UserForm.password)
                user.save()
            
            # Message de succès et redirection
                messages.success(request, "Utilisateur créé avec succès.")
                return redirect('success')

def success(request):
    return render(request, 'sucess.html')

        


# Create your views here.
