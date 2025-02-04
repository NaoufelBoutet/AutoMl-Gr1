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
    path('home/',autoML_views.espace_personel,name='perso'),
    path('sucess/',auth_user_views.success, name='success'),    
    path('home/import_data_home/', import_donnee_views.home_data, name='home_data'),
    path('home/<str:project_name>/upload_csv/',import_donnee_views.upload_csv,name='upload_csv'),
    path('home/project/',import_donnee_views.liste_project, name='liste_project'),
    path('home/creer_project/',import_donnee_views.creer_project, name='creer_project'),
    path('home/project/<str:project_name>/',import_donnee_views.project, name='project'),
    path('home/project/<str:project_name>/processing/<str:filename>/',import_donnee_views.process_dataset, name='process_dataset'),
    path('home/project/<str:project_name>/data_viz/<str:filename>/',import_donnee_views.viz_data, name='viz_data'),
    path('home/project/<str:project_name>/ML/<str:filename>/',import_donnee_views.ML, name='ML'),
    path('get_task_progress/<task_id>/', import_donnee_views.get_task_progress, name='get_task_progress'),
    path('clear_task_id/', import_donnee_views.clear_task_id, name="clear_task_id")
]
