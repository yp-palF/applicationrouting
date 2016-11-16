from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from cloudant.client import Cloudant
import datetime
from config import CLOUDANTPASSWORD, CLOUDANTUSERNAME
import json
import re

client = Cloudant(CLOUDANTUSERNAME, CLOUDANTPASSWORD, account=CLOUDANTUSERNAME)
client.connect()


# Create your views here.
@login_required
def home(request):
    DBAPPLICATIONS = client['applications']
    DBUSER = client['users']
    applicationList = DBAPPLICATIONS.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    applicationList1 = DBAPPLICATIONS.get_view_result('_design/fetch', 'byUsername')[:]
    for app in applicationList1:
        if request.user.username in app['value']['facultyList']:
            applicationList.append(app)
    for application in applicationList:
        application['class'] = application['id']
        application['id'] = "#" + application['id']
    # applicationList = [application1, application2, application3]
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    if user[0]['value']['designation'] == 'admin':
        return redirect('/admindashboard')
    return render(request, 'application/dashboard.html', {'user': user[0]['value'],
                                                          'applicationList': applicationList,
                                                          'notificationList': getNotification(request.user.username),
                                                          'i': getNotificationlength(request.user.username)})


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
        DBAPPLICATIONS = client['applications']
        DBACTIVITYLOG = client['activitylog']
        string = 'You created an application named ' + title + '.'
        dateCreated1 = str(datetime.datetime.strftime(datetime.datetime.now(), '%B %d, %Y, %H:%M %p'))
        DBACTIVITYLOG.create_document({'string': string, 'type': 'newapplication',
                                       'username': request.user.username,
                                       'date': dateCreated1})
        DBAPPLICATIONS.create_document(newApplication)
        applicationList = DBAPPLICATIONS.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        for app in applicationList:
            if app['value']['dateCreated'] == dateCreated:
                appId = app['id']
        for faculty in facultyList:
            text = request.user.username + " sent a new application " + newApplication['title']
            addNotification(text, faculty, "http://applicationrouting.eu-gb.mybluemix.net/applicationDetail/" + appId, "create")
        return redirect('/dashboard')


def mainpage(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    return render(request, 'application/main.html')


def logoutUser(request):
    logout(request)
    return redirect('/')


@login_required
def activitylog(request):
    DBACTIVITYLOG = client['activitylog']
    activities = DBACTIVITYLOG.get_view_result('_design/fetch', 'byDate')
    activityList = []
    user = request.user.username
    for activity in activities:
        if activity['value']['username'] == user:
            activityList.append(activity)
    activityList.reverse()
    return render(request, 'application/activitylog.html', {'user': request.user.username,
                                                            'activityList': activityList})


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
        print(application)
        status = "hide"
        for faculty in application['facultyList']:
            if faculty == request.user.username and application['status'] == "Disapproved":
                status = "Disapproved"
                break
            elif request.user.username == application['nextBy']:
                status = "yourTurn"
                break
            elif request.user.username == faculty:
                status = "Approved"
                break
            elif faculty == application['nextBy']:
                break
        return render(request, 'application/applicationDetail.html', {
            'user': user[0]['value'], 'application': application, 'appId': appId,
            'commentList': commentList, 'status': status})


@login_required
def editProfile(request):
    if request.method == "GET":
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        return render(request, 'application/editProfile.html', {'user': user[0]['value']})
    else:
        # Saving in cloudant
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        user = DBUSER[user[0]['id']]
        user['collegeName'] = request.POST['collegename']
        user['password'] = request.POST['password']
        user['dob'] = request.POST['dob']
        user['gender'] = request.POST['gender']
        user['motto'] = request.POST['motto']
        user['designation'] = 'User'
        user.save()
        DBACTIVITYLOG = client['activitylog']
        string = 'You edited your profile.'
        date = str(datetime.datetime.strftime(datetime.datetime.now(), '%B %d, %Y, %H:%M %p'))
        DBACTIVITYLOG.create_document({'string': string, 'type': 'editprofile',
                                       'username': request.user.username,
                                       'date': date})
        return redirect('/profile')


@login_required
def profile(request):
    if request.method == "GET":
        DBUSER = client['users']
        user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
        print(request.user.username)
        return render(request, 'application/profile.html', {'user': user[0]['value']})


@login_required
def faculty(request):
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    memberList = DBUSER.get_view_result('_design/fetch', 'byDesignation')['Faculty'][:]
    return render(request, 'application/faculty.html', {'user': user[0]['value'], 'memberList': memberList})


@login_required
def gymkhana(request):
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    memberList = DBUSER.get_view_result('_design/fetch', 'byDesignation')['Gymkhana'][:]
    return render(request, 'application/gymkhana.html', {'user': user[0]['value'], 'memberList': memberList})


@login_required
def student(request):
    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    memberList = DBUSER.get_view_result('_design/fetch', 'byDesignation')['Student'][:]
    return render(request, 'application/student.html', {'user': user[0]['value'], 'memberList': memberList})


@login_required
def admindashboard(request):
    if request.method == "GET":
        DBUSER = client['users']
        usernameView = DBUSER.get_view_result('_design/fetch', 'byUsername')
        user = usernameView[request.user.username]
        desigView = DBUSER.get_view_result('_design/fetch', 'byDesignation')
        userList = desigView['User'][:]
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
    DBCOMMENT = client['comments']
    DBAPPLICATIONS = client['applications']

    DBUSER = client['users']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    picUrl = user[0]['value']['picUrl']
    dateCreated = str(datetime.datetime.strftime(datetime.datetime.now(), '%B %d, %Y, %H:%M %p'))
    DBACTIVITYLOG = client['activitylog']
    title = DBAPPLICATIONS[appId]['title']
    string = 'You commented on ' + title + '.'
    DBACTIVITYLOG.create_document({'string': string, 'type': 'comment',
                                   'username': request.user.username,
                                   'date': dateCreated})
    DBCOMMENT.create_document({'appId': appId, 'body': request.POST['body'],
                               'username': request.user.username, 'picUrl': picUrl,
                               'dateCreated': dateCreated})
    facultyList = DBAPPLICATIONS[appId]['facultyList']
    text = request.user.username + " commented on " + title
    for faculty in facultyList:
        if faculty is not request.user.username:           
            addNotification(text, faculty, "http://applicationrouting.eu-gb.mybluemix.net/applicationDetail/" + appId, "comment")
    if DBAPPLICATIONS[appId]['from'] is not request.user.username:
        addNotification(text, DBAPPLICATIONS[appId]['from'], "http://applicationrouting.eu-gb.mybluemix.net/applicationDetail/" + appId, "comment")
    return redirect('/applicationDetail/' + appId)


@login_required
def searchby(request):
    DBAPPLICATIONS = client['applications']
    DBACTIVITYLOG = client['activitylog']
    applications = DBAPPLICATIONS.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    query = ''
    query = request.GET.get("search")
    print(query)
    string = 'You searched ' + query + '.'
    date = str(datetime.datetime.strftime(datetime.datetime.now(), '%B %d, %Y, %H:%M %p'))
    DBACTIVITYLOG.create_document({'string': string, 'type': 'search',
                                   'username': request.user.username,
                                   'date': date})
    i = 0
    searchlist = []
    for application in applications:
        if re.search(query, application['value']['title'], re.IGNORECASE):
            searchlist.append(application)
            i += 1
    return render(request, 'application/search.html', {'user': request.user.username,
                                                       'searchList': searchlist, 'i': i})


def facultyAction(request, appId):
    DBAPPLICATIONS = client['applications']
    application = DBAPPLICATIONS[appId]
    if request.POST['submit'] == "Approved":
        facultyList = DBAPPLICATIONS[appId]['facultyList']
        text = request.user.username + " approved an application " + application['title']
        for faculty in facultyList:
            if faculty is not request.user.username:           
                addNotification(text, faculty, "http://applicationrouting.eu-gb.mybluemix.net/applicationDetail/" + appId, "approve")
        if DBAPPLICATIONS[appId]['from'] is not request.user.username:
            addNotification(text, DBAPPLICATIONS[appId]['from'], "http://applicationrouting.eu-gb.mybluemix.net/applicationDetail/" + appId, "approve")
        idx = application['facultyList'].index(application['nextBy'])
        if (idx + 1) != len(application['facultyList']):
            application['nextBy'] = application['facultyList'][idx + 1]
            text = request.user.username + " forwarded an application " + application['title']
            addNotification(text, application['nextBy'], "http://applicationrouting.eu-gb.mybluemix.net/applicationDetail/" + appId, "forward")
        else:
            application['status'] = request.POST['submit']
            application['nextBy'] = 'Its Over!!!'
    else:
        application['status'] = request.POST['submit']
        facultyList = DBAPPLICATIONS[appId]['facultyList']
        text = request.user.username + " disapproved an application " + application['title']
        for faculty in facultyList:
            if faculty is not request.user.username:           
                addNotification(text, faculty, "http://applicationrouting.eu-gb.mybluemix.net/applicationDetail/" + appId, "disapprove")
        if DBAPPLICATIONS[appId]['from'] is not request.user.username:
            addNotification(text, DBAPPLICATIONS[appId]['from'], "http://applicationrouting.eu-gb.mybluemix.net/applicationDetail/" + appId, "disapprove")
    
    application.save()
    return redirect('/applicationDetail/' + appId)


@login_required
def sentApplications(request):
    DBAPPLICATIONS = client['applications']
    DBUSER = client['users']
    DBACTIVITYLOG = client['activitylog']
    if request.method == "POST":
        if request.POST['submit'] == 'Delete':
            for appId in request.POST.getlist('applicationList'):
                doc = DBAPPLICATIONS[appId]
                title = doc['title']
                doc.delete()
                string = 'You deleted a sent application named ' + title + '.'
                date = str(datetime.datetime.strftime(datetime.datetime.now(), '%B %d, %Y, %H:%M %p'))
                DBACTIVITYLOG.create_document({'string': string, 'type': 'delete',
                                               'username': request.user.username,
                                               'date': date})
        return redirect('/sentApplications')
    applicationList = DBAPPLICATIONS.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    for application in applicationList:
        application['class'] = application['id']
        application['id'] = "#" + application['id']
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    return render(request, 'application/sentapplications.html', {'user': user[0]['value'],
                                                                 'applicationList': applicationList})


def deleteUser(request):
    DBUSERS = client['users']
    user = DBUSERS[request.POST['userId']]
    user.delete()
    return redirect('/admindashboard')


def editDesignation(request):
    DBUSERS = client['users']
    user = DBUSERS[request.POST['userId']]
    facultyList = ['Director', 'Dean Academics', 'Dean Student Affair', 'Cultural Council Mentor',
                   'Sports Council Mentor', 'Sci. and Tech Council Mentor', 'Registrar']
    gymkhanaList = ['Student President', 'Cultural G.Sec.', 'Sports G.Sec.', 'Sci&Tech G.Sec.']
    if request.POST['designation'] in facultyList:
        user['designation'] = 'Faculty'
        user['post'] = request.POST['designation']
    elif request.POST['designation'] in gymkhanaList:
        user['designation'] = 'Gymkhana'
        user['post'] = request.POST['designation']
    else:
        user['designation'] = 'Student'
    user.save()
    text = "Admin assigned you designation " + user['designation']
    addNotification(text, user['username'], "http://applicationrouting.eu-gb.mybluemix.net/profile", "designation")
    return redirect(request.POST['next'])


def addNotification(text, user, link, typeApp):
    DBNOTIFICATION = client['notifications']
    dateCreated = str(datetime.datetime.strftime(datetime.datetime.now(), '%B %d, %Y, %H:%M %p'))
    date = str(datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y, %H:%M %p'))
    DBNOTIFICATION.create_document({'text': text, 'to': user, 'dateCreated': dateCreated,
                                    'read': "false", 'link': link, 'type': typeApp, 'date': date})


def getNotification(username):
    DBNOTIFICATION = client['notifications']
    notificationlist = DBNOTIFICATION.get_view_result('_design/fetch', 'byDate')
    notificationList = []
    for notification in notificationlist:
        if notification['value']['to'] == username and notification['value']['read'] == "false":
            notificationList.append(notification)
    notificationList.reverse()
    notificationList = notificationList[:6]
    return notificationList

def getNotificationlength(username):
    DBNOTIFICATION = client['notifications']
    notificationlist = DBNOTIFICATION.get_view_result('_design/fetch', 'byDate')
    notificationList = []
    i = 0
    for notification in notificationlist:
        if notification['value']['to'] == username and notification['value']['read'] == "false":
            notificationList.append(notification)
            i += 1
    return i

def read(request, notifyId):
    if request.method == "GET":
        DBNOTIFICATION = client['notifications']
        notification = DBNOTIFICATION[notifyId]
        notification['read'] = 'true'
        notification.save()
        return redirect(notification['link'])

def notifications(request):
    DBNOTIFICATION = client['notifications']
    notificationlist = DBNOTIFICATION.get_view_result('_design/fetch', 'byDate')
    notificationList = []
    for notification in notificationlist:
        if notification['value']['to'] == request.user.username and notification['value']['read'] == "false":
            notificationList.append(notification)
    notificationList.reverse()
    return render(request, 'application/notification.html', {'user': request.user.username,
                                                              'notificationList': notificationList,
                                                              'i': getNotificationlength(request.user.username)})


def pdfPage(request, appId):
    DBAPPLICATIONS = client['applications']
    app = DBAPPLICATIONS[appId]
    DBUSERS = client['users']
    facultyList = []
    view = DBUSERS.get_view_result('_design/fetch', 'byUsername')
    for user in app['facultyList']:
        result = view[user]
        facultyList.append({'fullName': result[0]['value']['fullName'], 'post': result[0]['value']['post']})
    return render(request, 'application/pdf.html', {'application': app, 'facultyList': facultyList})


def moveToTrash(request):
    DBACTIVITYLOG = client['activitylog']
    DBAPPLICATIONS = client['applications']
    DBTRASH = client['trash']
    for appId in request.POST.getlist('applicationList'):
        doc = DBAPPLICATIONS[appId]
        title = doc['title']
        DBTRASH.create_document(doc)
        doc.delete()
        string = 'You deleted an application named ' + title + '.'
        date = str(datetime.datetime.strftime(datetime.datetime.now(), '%B %d, %Y, %H:%M %p'))
        DBACTIVITYLOG.create_document({'string': string, 'type': 'delete',
                                       'username': request.user.username,
                                       'date': date})
    return redirect('/dashboard')


def restore(request):
    print("AD___________________________________________________________________")
    DBAPPLICATIONS = client['applications']
    DBTRASH = client['trash']
    for appId in request.POST.getlist('applicationList'):
        doc = DBTRASH[appId]
        DBAPPLICATIONS.create_document(doc)
        doc.delete()
    return redirect('/trash')


def deleteForever(request):
    DBTRASH = client['trash']
    for appId in request.POST.getlist('applicationList'):
        doc = DBTRASH[appId]
        doc.delete()
    return redirect('/trash')


def trash(request):
    DBTRASH = client['trash']
    DBUSER = client['users']
    applicationList = DBTRASH.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    applicationList1 = DBTRASH.get_view_result('_design/fetch', 'byUsername')[:]
    for app in applicationList1:
        if request.user.username in app['value']['facultyList']:
            applicationList.append(app)
    for application in applicationList:
        application['class'] = application['id']
        application['id'] = "#" + application['id']
    # applicationList = [application1, application2, application3]
    user = DBUSER.get_view_result('_design/fetch', 'byUsername')[request.user.username]
    if user[0]['value']['designation'] == 'admin':
        return redirect('/admindashboard')
    return render(request, 'application/trash.html', {'user': user[0]['value'],
                                                          'applicationList': applicationList,
                                                          'notificationList': getNotification(request.user.username)})
