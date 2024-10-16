"""
URL configuration for Projet_Plateforme project.
Laurence Berville 2024

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/

"""
from django.contrib import admin
from django.urls import path
from polls import views as polls_views
from Exploration_donnees import views as Explo_views # donner un alias pour ne pas mélanger les "views"
from Authentification  import views as Authentification_views 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', Explo_views.hello, name="hello"), # alias et nom de la fonction, ici "hello"
    path('import_csv/', Explo_views.import_csv, name='import_csv'),
    path('analyses/', Explo_views.analyses, name = 'analyses'),
    path('inscriptions/', Authentification_views.inscriptions , name='inscription'),
    path('login/', Authentification_views.login_view, name='login'),  # Utilisation de LoginView

    path('about_us/', polls_views.about_us, name= "about_us"), # aide
    path('contact_us/', polls_views.contact,name= 'contact_us'),
    path('contact_us/success/', polls_views.success_view, name='contact_success'),

    path('help/', polls_views.help, name= 'help'),
]

