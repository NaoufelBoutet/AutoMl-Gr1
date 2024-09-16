from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserForm
from django.http import HttpResponse

def show_login(request):
    return render(request, 'login.html')

def show_sign(request): 
    return render(request, 'sign.html')

def sign_in(request):
    if request.method=='POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Récupérer les données validées via cleaned_data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            else:
                # Créer l'utilisateur
                user = User.objects.create_user(username=username, password=password)
                user.save()
            
            # Message de succès et redirection
                messages.success(request, "Utilisateur créé avec succès.")
                return redirect('success')
        else:
            return HttpResponse("Hello, World!")
    return render(request, 'sign.html', {'form': form})

def success(request):
    return render(request, 'sucess.html')

        


# Create your views here.
