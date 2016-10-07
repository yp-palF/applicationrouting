from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, 'application/dashboard.html', {'user': request.POST['username']})


def login(request):
    return render(request, 'application/login.html')


def createApplication(request):
    return render(request, 'application/createApplication.html', {'user': request.POST['username']})


def mainpage(request):
    return render(request, 'application/main.html')


def allApplication(request):
    return render(request, 'application/allapplication.html')
