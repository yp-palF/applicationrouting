from django.http import HttpResponse
from application.views import client
import json
from django.contrib.auth.models import User


# Create your views here.
def resetCloudantDB(request):
    client.delete_database('users')
    client.delete_database('applications')
    client.delete_database('comments')
    client.delete_database('activitylog')
    client.delete_database('notifications')
    client.delete_database('trash')
    DB1 = client.create_database('users')
    DB2 = client.create_database('applications')
    DB3 = client.create_database('comments')
    DB4 = client.create_database('activitylog')
    DB5 = client.create_database('notifications')
    DB6 = client.create_database('trash')
    #populateData('a')
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
    DBNOTIFICATION = client['notifications']
    DBTRASH = client['trash']
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "byEmail": {
                "map": "function(doc) { if (doc.email) { emit(doc.email, doc);} }""",
            },
            "byUsername": {
                "map": "function(doc) { if (doc.username) { emit(doc.username, doc);} }""",
            },
            "byDesignation": {
                "map": """function(doc) {
                    if (doc.designation) {
                        emit(doc.designation, doc);
                    }
                }""",
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
    DBCOMMENTS = client['comments']
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "byAppId": {
                "map": "function(doc) { if (doc.appId) { emit(doc.appId, doc);} }""",
            }
        },
        "language": "javascript"
    }
    DBCOMMENTS.create_document(designDoc)
    DBACTIVITYLOG = client['activitylog']
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "byUsername": {
                "map": """function(doc) {
                    if (doc.username) {
                        emit(doc.username, doc);
                    }
                }""",
            },
            "byDate": {
                "map": """function(doc) {
                    if (doc.date) {
                        emit(doc.date, doc);
                    }
                }""",
            }
        },
        "language": "javascript"
    }
    DBACTIVITYLOG.create_document(designDoc)
    designDoc = {
        "_id": "_design/fetch",
        "views": {
            "byUsername": {
                "map": """function(doc) {
                    if (doc.username) {
                        emit(doc.username, doc);
                    }
                }""",
            },
            "byDate": {
                "map": """function(doc) {
                    if (doc.date) {
                        emit(doc.date, doc);
                    }
                }""",
            }
        },
        "language": "javascript"
    }
    DBNOTIFICATION.create_document(designDoc)
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
    DBTRASH.create_document(designDoc)

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


def displayUsers(request):
    return HttpResponse(User.objects.all())


def setUserPassword(request):
    DBUSER = client['users']
    userList = DBUSER.get_view_result('_design/fetch', 'byUsername')[:]
    for user in userList:
        username = user['value']['username']
        email = user['value']['email']
        if username == 'Admin':
            password = 'admin'
        elif username == 'Student':
            password = 'student'
        else:
            password = username.lower()
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
