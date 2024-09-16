from django.shortcuts import render
def home(request):
    return render(request, 'accueil.html')

# Create your views here.
