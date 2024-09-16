from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader


def home(request):
    return render(redirect,'test1.html', context = {'message':'1'})
# Create your views here.
