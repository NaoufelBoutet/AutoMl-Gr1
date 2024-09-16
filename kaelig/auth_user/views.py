from django.shortcuts import render

def login(request):
    return render(request, 'login.html')

def sign(request): 
    return render(request, 'sign.html')
# Create your views here.
