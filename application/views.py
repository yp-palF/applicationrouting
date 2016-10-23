from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from cloudant.client import Cloudant

from config import CLOUDANTPASSWORD, CLOUDANTUSERNAME

client = Cloudant(CLOUDANTUSERNAME, CLOUDANTPASSWORD, account=CLOUDANTUSERNAME)
client.connect()


# Create your views here.
@login_required
def home(request):
    DBAPPLICATIONS = client['applications']
    if request.method == "POST":
        if request.POST['submit'] == 'Delete':
            print(request.POST.getlist('applicationList'))
            for appId in request.POST.getlist('applicationList'):
                print(appId)
                doc = DBAPPLICATIONS[appId]
                doc.delete()
        return redirect('/dashboard')
    applicationList = DBAPPLICATIONS.get_view_result('_design/fetch', 'byAppId')[:]
    for application in applicationList:
        application['class'] = application['id']
        application['id'] = "#" + application['id']
    # applicationList = [application1, application2, application3]
    return render(request, 'application/dashboard.html', {'username': request.user.username,
                                                          'applicationList': applicationList})



@csrf_protect
def loginUser(request):
    if request.method == 'GET':
        return render(request, 'application/login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/dashboard')
        else:
            print("INVALID")
            return redirect('/login')


@csrf_protect
def signup(request):
    if request.method == 'GET':
        return render(request, 'application/signup.html')
    else:
        username = request.POST['usernamesignup']
        email = request.POST['emailsignup']
        password = request.POST['passwordsignup']
        # Saving in sqlite
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        # Saving in cloudant
        DBUSERS = client['users']
        print (DBUSERS.all_docs())
        newUser = {'username': username, 'email': email}
        DBUSERS.create_document(newUser)
        return redirect('/login')


@login_required
def createApplication(request):
    if request.method == "GET":
        return render(request, 'application/createApplication.html', {'username': request.user.username})
    else:
        print(request.POST)
        title = request.POST['text-680']
        appType = request.POST.get('type', 'General')
        status = 'Pending'
        dueDate = request.POST['dead_line']
        nextBy = request.POST.getlist('checkbox-465[]')[0]
        facultyList = request.POST.getlist('checkbox-465[]')
        subject = request.POST['textarea-398'].strip()
        print(title)
        print(appType)
        print(status)
        print(dueDate)
        print(nextBy)
        print(facultyList)
        print(subject)
        newApplication = {'title': title, 'type': appType, 'status': status, 'dueDate': dueDate, 'nextBy': nextBy, 'subject': subject}
        DBAPPLICATIONS = client['applications']
        DBAPPLICATIONS.create_document(newApplication)




def mainpage(request):
    return render(request, 'application/main.html')


@login_required
def allApplication(request):
    DBAPPLICATIONS = client['applications']
    applicationList = DBAPPLICATIONS.get_view_result('_design/fetch', 'byAppId')[:]
    return render(request, 'application/allapplication.html', {'applicationList': applicationList})


def logoutUser(request):
    logout(request)
    return redirect('/')
