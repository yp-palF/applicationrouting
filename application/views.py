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
    application1 = {'id': '#collapse1', 'class': 'collapse1', 'title': 'Regarding LT9', 'type': 'academic', 'status': 'pending',
                   'dueDate': '11/10/16', 'nextBy': 'Ajit Patel', 'subject': 'hui hiuh huashdalkdhfad kahfhd hasdkj hgg ash hjsagkdkj ashfgsa sakjfgjhddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd dddddddddddddddddddddddddddddddddddddd kjdfaskfjdfjsga fas fkjanf kahf gafk'}
    application2 = {'id': '#collapse2', 'class': 'collapse2', 'title': 'Regarding LT9', 'type': 'academic', 'status': 'pending',
                   'dueDate': '11/10/16', 'nextBy': 'Ajit Patel', 'subject': 'hui hiuh huashdalkdhfad kahfhd hasdkj hgg ash hjsagkdkj ashfgsa sakjfgjhsagfash fkjfdg fkjsnajfdjfgask kjdfaskfjdfjsga fas fkjanf kahf gafk'}
    application3 = {'id': '#collapse3', 'class': 'collapse3', 'title': 'Regarding LT9', 'type': 'academic', 'status': 'pending',
                   'dueDate': '11/10/16', 'nextBy': 'Ajit Patel', 'subject': 'hui hiuh huashdalkdhfad kahfhd hasdkj hgg ash hjsagkdkj ashfgsa sakjfgjhsagfash fkjfdg fkjsnajfdjfgask kjdfaskfjdfjsga fas fkjanf kahf gafk'}
    application4 = {'id': '#collapse4', 'class': 'collapse4', 'title': 'Regarding LT9', 'type': 'academic', 'status': 'pending',
                   'dueDate': '11/10/16', 'nextBy': 'Ajit Patel', 'subject': 'hui hiuh huashdalkdhfad kahfhd hasdkj hgg ash hjsagkdkj ashfgsa sakjfgjhsagfash fkjfdg fkjsnajfdjfgask kjdfaskfjdfjsga fas fkjanf kahf gafk'}
    application5 = {'id': '#collapse5', 'class': 'collapse5', 'title': 'Regarding LT9', 'type': 'academic', 'status': 'pending',
                   'dueDate': '11/10/16', 'nextBy': 'Ajit Patel', 'subject': 'hui hiuh huashdalkdhfad kahfhd hasdkj hgg ash hjsagkdkj ashfgsa sakjfgjhsagfash fkjfdg fkjsnajfdjfgask kjdfaskfjdfjsga fas fkjanf kahf gafk'}
    application6 = {'id': '#collapse6', 'class': 'collapse6', 'title': 'Regarding LT9', 'type': 'academic', 'status': 'pending',
                   'dueDate': '11/10/16', 'nextBy': 'Ajit Patel', 'subject': 'hui hiuh huashdalkdhfad kahfhd hasdkj hgg ash hjsagkdkj ashfgsa sakjfgjhsagfash fkjfdg fkjsnajfdjfgask kjdfaskfjdfjsga fas fkjanf kahf gafk'}
    applicationList = [application1, application2, application3, application4, application5, application6]
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
        return render(request, 'application/createApplication.html', {'user': request.user.username})
    else:
        print(request.POST)


def mainpage(request):
    DBUSERS = client['users']
    print (DBUSERS.get_view_result('_design/fetch', 'by_email')['saurav@gm.c'])
    return render(request, 'application/main.html')


@login_required
def allApplication(request):
    DBAPPLICATIONS = client['applications']
    applicationList = DBAPPLICATIONS.get_view_result('_design/fetch', 'by_userid')[:]
    print (applicationList)
    return render(request, 'application/allapplication.html', {'applicationList': applicationList})


def logoutUser(request):
    logout(request)
    return redirect('/')
