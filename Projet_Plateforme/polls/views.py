from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , redirect
from Exploration_donnees.models import Utilisateurs
import csv
#from django.contrib import messages
import os  # Nécessaire pour gérer les chemins de fichiers
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponse

def about_us(request):
    return HttpResponse('<h1>À propos de nous </h1> <p>Nous adorons les graphs, les statistiques et les modeles</p>')

def contact(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        # Vous pouvez maintenant envoyer un email ou stocker ces informations dans une base de données
        send_mail(
            subject=f"Contact Form: {subject}",
            message=f"Message from {name} ({email}):\n\n{message}",
            from_email=email,
            recipient_list=['support@yourdomain.com'],  # Changez à votre email de destination
            fail_silently=False,
        )
        return HttpResponseRedirect(reverse('contact_success'))  # Redirige vers une page de succès
    return render(request, 'contact-us.html')

def success_view(request):
    return render(request, 'success.html', {'message': "Thank you for contacting us!"})


def help(request):
    return HttpResponse(" Aide et Exemples.")
