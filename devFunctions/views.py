from django.shortcuts import render
from django.http import HttpResponse
from application.views import client
import json


# Create your views here.
def resetCloudantDB(request):
    DB = client.create_database('users')
    if DB.exists():
        return HttpResponse('SUCCESS!!')


def createDesignDoc(request):
    DBUSERS = client['users']
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "by_email": {
                "map": """function(doc) {
                    if (doc.ts) {
                        emit(doc.email, null);
                    }
                }"""
            }
        },
        "language": "javascript"
    }
    DBUSERS.create_document(designDoc)


def populateData(request):
    DBUSERS = client['users']
    with open('devFunctions/users.json') as data_file:
        data = json.load(data_file)
        for user in data:
            DBUSERS.create_document(user)
