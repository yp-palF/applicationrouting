from django.http import HttpResponse
from application.views import client
import json


# Create your views here.
def resetCloudantDB(request):
    client.delete_database('users')
    client.delete_database('applications')
    DB1 = client.create_database('users')
    DB2 = client.create_database('applications')
    populateData('a')
    createDesignDoc('a')
    if DB1.exists() and DB2.exists():
        return HttpResponse('SUCCESS!!')


def createDesignDoc(request):
    DBUSERS = client['users']
    DBAPPLICATIONS = client['applications']
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "byEmail": {
                "map": """function(doc) {
                    if (doc.email) {
                        emit(doc.email, doc);
                    }
                }""",
                "reduce": "_count",
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
