"""
URL configuration for autoML2 project.

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
from django.urls import include, path
from auth_user import views as auth_user_views
from main import views as autoML_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', autoML_views.home, name='home'),
    path('login/',auth_user_views.show_login, name='show_login'),
    path('sign/', auth_user_views.show_sign, name='show_sign'),
    path('users/', auth_user_views.sign_in, name='sign_in'),
    path('connect/',auth_user_views.login, name='login'),
    path('sucess/',auth_user_views.success, name='success'), 
    path('__debug__/', include('debug_toolbar.urls')),
    path('home/',autoML_views.espace_personel,name='perso'),
    path('home/project/',autoML_views.liste_project, name='liste_project'),
    path('home/creer_project/',autoML_views.creer_project, name='creer_project'),
    path('home/project/<str:project_name>/',autoML_views.project, name='project'),
]
