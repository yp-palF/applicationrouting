from django.http import HttpResponse
from application.views import client
import json
from django.contrib.auth.models import User


# Create your views here.
def resetCloudantDB(request):
    client.delete_database('users')
    client.delete_database('applications')
    DB1 = client.create_database('users')
    DB2 = client.create_database('applications')
    populateData('a')
    createDesignDoc('a')
    deleteSqlite('a')
    if DB1.exists() and DB2.exists():
        return HttpResponse('SUCCESS!!')


def deleteSqlite(request):
    userList = User.objects.all()
    for user in userList:
        user.delete()
    return HttpResponse('SUCCESS!!')


def createDesignDoc(request):
    DBUSERS = client['users']
    DBAPPLICATIONS = client['applications']
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "byEmail": {
                "map": "function(doc) { if (doc.email) { emit(doc.email, doc);} }""",
            },
            "byUsername": {
                "map": "function(doc) { if (doc.username) { emit(doc.username, doc);} }""",
            }
        },
        "language": "javascript"
    }
    DBUSERS.create_document(designDoc)
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "byAppId": {
                "map": """function(doc) {
                    if (doc._id) {
                        emit(doc._id, doc);
                    }
                }""",
            },
            "byUsername": {
                "map": """function(doc) {
                    if (doc.from) {
                        emit(doc.from, doc);
                    }
                }""",
            }
        },
        "language": "javascript"
    }
    DBAPPLICATIONS.create_document(designDoc)


def populateData(request):
    DBUSERS = client['users']
    with open('devFunctions/users.json') as data_file:
        data = json.load(data_file)
        for user in data:
            DBUSERS.create_document(user)
    DBAPPLICATIONS = client['applications']
    with open('devFunctions/applications.json') as data_file:
        data = json.load(data_file)
        for application in data:
            DBAPPLICATIONS.create_document(application)
