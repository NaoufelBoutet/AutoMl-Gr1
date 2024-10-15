"""
URL configuration for Projet_Plateforme project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from polls import views as polls_views
from Exploration_donnees import views as Explo_views # donner un alias pour ne pas mélanger les "views"
from Authentification  import views as Authentification_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', Explo_views.hello), # alias et nom de la fonction, ici "hello"
    path('about_us/', polls_views.about_us),
    path('contact_us/', polls_views.contact_us),
    path('help/', polls_views.help),
    path('import_csv/', Explo_views.import_csv, name='import_csv'),
    path('inscriptions/', Authentification_views.inscriptions , name='inscription'),
]

