from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    return render(request,'index.html')

def generate_blog(request):
    pass

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        password = request.POST.get('password')
        if not username or not password:
            error_message = "Username and password are required"
            return render(request, 'login.html', {'error_message': error_message})
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Username or password is incorrect"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeatPassword = request.POST.get('repeatPassword')

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username,email,password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = "username already exists"
                return render(request,'signup.html',{'error_message':error_message})

        else:
            error_message = "passwords do not match"
            return render(request,'signup.html',{'error_message':error_message})
    return render(request,'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')
    

 