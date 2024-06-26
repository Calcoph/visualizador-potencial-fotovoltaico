from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import HttpRequest, HttpResponse

def create_user(request: HttpRequest):
    user = request.POST.get("user")
    password = request.POST.get("password")

    user = User.objects.create_user(username=user, password=password)
    user.save()

def change_password(request: HttpRequest):
    user = request.POST.get("user")
    password = request.POST.get("password")

    user = User.objects.get(username=user)
    user.set_password(password)
    user.save()

def login(request: HttpRequest):
    user = request.GET.get("username")
    password = request.GET.get("password")

    logged_user = authenticate(username=user,password=password)

    return HttpResponse(logged_user.get_username())

def register(request: HttpRequest):
    return HttpResponse("TODO")
