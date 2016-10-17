from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from cloudant.client import Cloudant

from config import CLOUDANTPASSWORD, CLOUDANTUSERNAME, CLOUDANTACCOUNT
 
client = Cloudant(CLOUDANTUSERNAME, CLOUDANTPASSWORD, account=CLOUDANTUSERNAME)
client.connect()
# Create your views here.
@login_required
def home(request):
    return render(request, 'application/dashboard.html', {'user': request.user.username})


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
        newUser = {'username': username, 'email': email}
        doc = DBUSERS.create_document(newUser)
        return redirect('/login')

@login_required
def createApplication(request):
    return render(request, 'application/createApplication.html', {'user': request.POST['username']})


def mainpage(request):
    return render(request, 'application/main.html')

@login_required
def allApplication(request):
    return render(request, 'application/allapplication.html')


def logoutUser(request):
    logout(request)
    return redirect('/')