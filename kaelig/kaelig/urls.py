"""
URL configuration for kaelig project.

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
from django.urls import include, path
from autoML import views as autoML_views
from auth_user import views as auth_user_views
from import_donnee import views as import_donnee_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', autoML_views.home, name='home'),
    path('login/',auth_user_views.show_login, name='show_login'),
    path('sign/', auth_user_views.show_sign, name='show_sign'),
    path('users/', auth_user_views.sign_in, name='sign_in'),
    path('connect/',auth_user_views.login, name='login'),
    path('username/<str:username>/',autoML_views.espace_personel,name='perso'),
    path('sucess/',auth_user_views.success, name='success'),    
    path('username/<str:username>/import_data_home/', import_donnee_views.home_data, name='home_data'),
    path('username/<str:username>/upload_csv/',import_donnee_views.upload_csv,name='upload_csv'),
    path('username/<str:username>/result_csv/',import_donnee_views.result_csv,name='result_csv'),
    path('username/<str:username>/browse_file/',import_donnee_views.browse_file, name='browse_file'),
    path('username/<str:username>/filename/<str:filename>',import_donnee_views.read_csv,name='read_csv'),
    path('username/<str:username>/filename/<str:filename>/html',import_donnee_views.df_to_html,name='df_to_html')
]
