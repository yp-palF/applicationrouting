from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from cloudant.client import Cloudant
import datetime
from config import CLOUDANTPASSWORD, CLOUDANTUSERNAME

client = Cloudant(CLOUDANTUSERNAME, CLOUDANTPASSWORD, account=CLOUDANTUSERNAME)
client.connect()


# Create your views here.
@login_required
def home(request):
    users = User.objects.all()
    DBAPPLICATIONS = client['applications']
    DBUSER = client['users']
    if request.method == "POST":
        if request.POST['submit'] == 'Delete':
            for appId in request.POST.getlist('applicationList'):
                doc = DBAPPLICATIONS[appId]
                doc.delete()
        return redirect('/dashboard')
    applicationList = DBAPPLICATIONS.get_view_result('_design/fetch', 'byAppId')[:]
    for application in applicationList:
        application['class'] = application['id']
        application['id'] = "#" + application['id']
    # applicationList = [application1, application2, application3]
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    return render(request, 'application/dashboard.html', {'user': user[0]['value'],
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
            return redirect('/login')


@csrf_exempt
def googleSignup(request):
    email = request.POST['email']
    DBUSER = client['users']
    newUser = DBUSER.get_view_result('_design/fetch', 'byEmail')[email]
    if len(newUser) != 0:
        # user already exists
        username = newUser[0]['value']['username']
        user = User.objects.get(username=username)
        login(request, user)
        return redirect('/dashboard')
    else:
        picUrl = request.POST['picUrl']
        fullName = request.POST['fullName']
        return render(request, 'application/signup.html', {'email': email, 'picUrl': picUrl, 'fullName': fullName})


@csrf_protect
def signup(request):
    if request.method == 'GET':
        return render(request, 'application/signup.html')
    else:
        username = request.POST['usernamesignup']
        email = request.POST['emailsignup']
        password = request.POST['passwordsignup']
        picUrl = request.POST['picUrl']
        fullName = request.POST['fullName']
        # Saving in sqlite
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        # Saving in cloudant
        DBUSERS = client['users']
        newUser = {'username': username, 'email': email, 'picUrl': picUrl, 'fullName': fullName}
        DBUSERS.create_document(newUser)
        return redirect('/login')


@login_required
def createApplication(request):
    if request.method == "GET":
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        return render(request, 'application/createApplication.html', {'user': user[0]['value']})
    else:
        title = request.POST['text-680']
        appType = request.POST.get('type', 'General')
        status = 'Pending'
        dueDate = request.POST['dead_line']
        nextBy = request.POST.getlist('checkbox-465[]')[0]
        facultyList = request.POST.getlist('checkbox-465[]')
        subject = request.POST['textarea-398'].strip()
        author = request.user.username
        dateCreated = str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d, %H:%M %p'))
        newApplication = {'from': author, 'title': title, 'type': appType, 'status': status,
                          'dueDate': dueDate, 'nextBy': nextBy, 'subject': subject,
                          'facultyList': facultyList, 'dateCreated': dateCreated}
        DBAPPLICATIONS = client['applications']
        DBAPPLICATIONS.create_document(newApplication)
        return redirect('/dashboard')


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


@login_required
def members(request):
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    return render(request, 'application/members.html', {'user': user[0]['value']})

@login_required
def applicationDetail(request, appId):
    if request.method == "GET":
        DBAPPLICATIONS = client['applications']
        application = DBAPPLICATIONS[appId]
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        return render(request, 'application/applicationDetail.html', {'user': user[0]['value'], 'application': application})
    else:
        DBAPPLICATIONS = client['applications']
        application = DBAPPLICATIONS[appId]
        application['status'] = request.POST['submit']
        application.save()
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        return render(request, 'application/applicationDetail.html', {'user': user[0]['value'], 'application': application})


@login_required
def editProfile(request):
    if request.method == "GET":
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        return render(request, 'application/editProfile.html',  {'user': user[0]['value']})