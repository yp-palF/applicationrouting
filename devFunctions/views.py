from django.shortcuts import render
from django.http import HttpResponse
from application.views import client

# Create your views here.
def resetCloudantDB(request):
    DB = client.create_database('router')
    if DB.exists():
        return  HttpResponse('SUCCESS!!')
