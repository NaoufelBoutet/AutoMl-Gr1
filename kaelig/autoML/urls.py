from django.urls import path
from autoML import views

urlpatterns = [
    path('home/', views.home, name='home'),
]