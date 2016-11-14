from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from cloudant.client import Cloudant
import datetime
from config import CLOUDANTPASSWORD, CLOUDANTUSERNAME
import json

client = Cloudant(CLOUDANTUSERNAME, CLOUDANTPASSWORD, account=CLOUDANTUSERNAME)
client.connect()


# Create your views here.
@login_required
def home(request):
    DBAPPLICATIONS = client['applications']
    DBUSER = client['users']
    if request.method == "POST":
        if request.POST['submit'] == 'Delete':
            for appId in request.POST.getlist('applicationList'):
                doc = DBAPPLICATIONS[appId]
                doc.delete()
        return redirect('/dashboard')
    applicationList = DBAPPLICATIONS.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    for application in applicationList:
        application['class'] = application['id']
        application['id'] = "#" + application['id']
    # applicationList = [application1, application2, application3]
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    if user[0]['value']['designation'] == 'admin':
        return redirect('/admindashboard')
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
            DBUSER = client['users']
            userList = DBUSER.get_view_result('_design/fetch', 'byUsername')[username]
            login(request, user)
            if userList[0]['value']['designation'] == 'admin':
                return redirect('/admindashboard')
            else:
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
        DBUSER = client['users']
        userList = DBUSER.get_view_result('_design/fetch', 'byUsername')[username]
        login(request, user)
        if userList[0]['value']['designation'] == 'admin':
            return redirect('/admindashboard')
        else:
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
        newUser = {'username': username, 'email': email, 'picUrl': picUrl, 'fullName': fullName, 'designation': 'User'}
        DBUSERS.create_document(newUser)
        return redirect('/login')


@login_required
def createApplication(request):
    if request.method == "GET":
        DBUSER = client['users']
        desigView = DBUSER.get_view_result('_design/fetch', 'byDesignation')
        facultyList = desigView['Faculty'][:]
        gymkhanaList = desigView['Gymkhana'][:]
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        return render(request, 'application/createApplication.html', {
            'user': user[0]['value'],
            'facultyList': facultyList,
            'gymkhanaList': gymkhanaList,
            'date': datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')})
    else:
        print(request.POST)
        title = request.POST['title']
        appType = request.POST.get('type', 'General')
        status = 'Pending'
        dueDate = request.POST['dueDate']
        nextBy = request.POST.getlist('facultyList')[0]
        facultyList = request.POST.getlist('facultyList')
        subject = request.POST['subject'].strip()
        priority = request.POST['priority']
        author = request.user.username
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        dateCreated = str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d, %H:%M %p'))
        newApplication = {'from': author, 'title': title, 'type': appType, 'status': status,
                          'dueDate': dueDate, 'nextBy': nextBy, 'subject': subject,
                          'facultyList': facultyList, 'dateCreated': dateCreated,
                          'picUrl': user[0]['value']['picUrl'], 'priority': priority}
        print(newApplication)
        DBAPPLICATIONS = client['applications']
        DBAPPLICATIONS.create_document(newApplication)
        return redirect('/dashboard')


def mainpage(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    return render(request, 'application/main.html')


def logoutUser(request):
    logout(request)
    return redirect('/')


@login_required
def members(request):
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    memberList = DBUSER.get_view_result('_design/fetch', 'byUsername')[:]
    return render(request, 'application/members.html', {'user': user[0]['value'], 'memberList': memberList})


@login_required
def applicationDetail(request, appId):
    if request.method == "GET":
        DBAPPLICATIONS = client['applications']
        application = DBAPPLICATIONS[appId]
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        DBCOMMENT = client['comments']
        commentList = DBCOMMENT.get_view_result('_design/fetch', 'byAppId')[appId]
        return render(request, 'application/applicationDetail.html', {'user': user[0]['value'], 'application': application, 'appId': appId, 'commentList': commentList})


@login_required
def editProfile(request):
    if request.method == "GET":
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        return render(request, 'application/editProfile.html',  {'user': user[0]['value']})
    else:
        # Saving in cloudant
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        #print(user)
        user = DBUSER[user[0]['id']]
        user['username'] = request.POST['username']
        user['email'] = request.POST['email']
        user['collegeName'] = request.POST['collegename']
        user['password'] = request.POST['password']
        user['fullName'] = request.POST['fullname']
        user['dob'] = request.POST['dob']
        user['gender'] = request.POST['gender']
        user['motto'] = request.POST['motto']
        user['designation'] = 'User'
        #user['picUrl'] = request.POST['dp']
        #print(request.POST['gender'])
        user.save()
        print(user)
        return redirect('/profile')


@login_required
def profile(request):
    if request.method == "GET":
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        return render(request, 'application/profile.html', {'user': user[0]['value']})


@login_required
def faculty(request, notification=None):
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    memberList = DBUSER.get_view_result('_design/fetch', 'byDesignation')['Faculty'][:]
    if len(notification) == 0:
        return render(request, 'application/faculty.html', {'user': user[0]['value'], 'memberList': memberList})
    else:
        return render(request, 'application/faculty.html', {'user': user[0]['value'], 'memberList': memberList, 'text': ("1 user designated as " + notification)})


@login_required
def gymkhana(request, notification=None):
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    memberList = DBUSER.get_view_result('_design/fetch', 'byDesignation')['Gymkhana'][:]
    if len(notification) == 0:
        return render(request, 'application/gymkhana.html', {'user': user[0]['value'], 'memberList': memberList})
    else:
        return render(request, 'application/gymkhana.html', {'user': user[0]['value'], 'memberList': memberList, 'text': ("1 user designated as " + notification)})


@login_required
def student(request, notification=None):
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    memberList = DBUSER.get_view_result('_design/fetch', 'byDesignation')['Student'][:]
    if len(notification) == 0:
        return render(request, 'application/student.html', {'user': user[0]['value'], 'memberList': memberList})
    else:
        return render(request, 'application/student.html', {'user': user[0]['value'], 'memberList': memberList, 'text': ("1 user designated as " + notification)})


@login_required
def admindashboard(request, notification=None):
    if request.method == "GET":
        DBUSER = client['users']
        usernameView = DBUSER.get_view_result('_design/fetch', 'byUsername')
        user = usernameView[request.user.username]
        desigView = DBUSER.get_view_result('_design/fetch', 'byDesignation')
        userList = desigView['User'][:]
        print (userList)
        if user[0]['value']['designation'] != 'admin':
            return redirect('/dashboard')
        total = len(usernameView[:])
        gymkhana = len(desigView['Gymkhana'][:])
        students = len(desigView['Student'][:])
        faculty = len(desigView['Faculty'][:])
        return render(
            request, 'application/admindashboard.html',
            {'user': user[0]['value'], 'newUserList': userList, 'total': total,
             'students': students, 'gymkhana': gymkhana, 'faculty': faculty,
             'designation': json.dumps(['Faculty', 'Admin', 'Gymkhana'])})


def comment(request, appId):
    print(request.POST)
    DBCOMMENT = client['comments']
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    picUrl = user[0]['value']['picUrl']
    dateCreated = str(datetime.datetime.strftime(datetime.datetime.now(), '%B %d, %Y, %H:%M %p'))
    DBCOMMENT.create_document({'appId': appId, 'body': request.POST['body'],
                               'username': request.user.username, 'picUrl': picUrl,
                               'dateCreated': dateCreated})
    return redirect('/applicationDetail/' + appId)


def facultyAction(request, appId):
    DBAPPLICATIONS = client['applications']
    application = DBAPPLICATIONS[appId]
    if request.POST['submit'] == "Approved":
        idx = application['facultyList'].index(application['nextBy'])
        if (idx + 1) != len(application['facultyList']):
            application['nextBy'] = application['facultyList'][idx + 1]
        else:
            application['status'] = request.POST['submit']
            application['nextBy'] = 'Its Over!!!'
    else:
        application['status'] = request.POST['submit']

    application.save()
    return redirect('/applicationDetail/' + appId)


def deleteUser(request):
    DBUSERS = client['users']
    user = DBUSERS[request.POST['userId']]
    user.delete()
    return redirect('/admindashboard')


def editDesignation(request):
    print(request.POST)
    DBUSERS = client['users']
    user = DBUSERS[request.POST['userId']]
    facultyList = ['Director', 'Dean Academics', 'Dean Student Affair', 'Cultural Council Mentor',
                   'Sports Council Mentor', 'Sci. and Tech Council Mentor', 'Registrar']
    gymkhanaList = ['Student President', 'Cultural G.Sec.', 'Sports G.Sec.', 'Sci&Tech G.Sec.']
    if request.POST['designation'] in facultyList:
        user['designation'] = 'Faculty'
        user['post'] = request.POST['designation']
        notification = 'Faculty'
    elif request.POST['designation'] in gymkhanaList:
        user['designation'] = 'Gymkhana'
        user['post'] = request.POST['designation']
        notification = 'Gymkhana'
    else:
        user['designation'] = 'Student'
        notification = 'Student'
    user.save()
    return redirect(request.POST['next'], notification=notification)
