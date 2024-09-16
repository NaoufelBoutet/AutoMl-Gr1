from django.shortcuts import render
from forms import UserForm

def show_login(request):
    return render(request, 'login.html')

def show_sign(request): 
    return render(request, 'sign.html')


# Create your views here.
