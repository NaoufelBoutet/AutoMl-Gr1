from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def home(request):
    template = loader.get_template('test1.html')
    return HttpResponse(template.render())
# Create your views here.
