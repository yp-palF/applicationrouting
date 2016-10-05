from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, 'application/dashboard.html', {'user': request.POST['username']})

def login(request):
    return render(request, 'application/login.html')
