from django.http import HttpResponse
from application.views import client
import json


# Create your views here.
def resetCloudantDB(request):
    DB1 = client.create_database('users')
    DB2 = client.create_database('applications')
    if DB1.exists() and DB2.exists():
        return HttpResponse('SUCCESS!!')


def createDesignDoc(request):
    DBUSERS = client['users']
    DBAPPLICATIONS = client['applications']
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "by_email": {
                "map": """function(doc) {
                    if (doc.email) {
                        emit(doc.email, null);
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
            "by_userid": {
                "map": """function(doc) {
                    if (doc.to) {
                        emit(doc.to, doc);
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
