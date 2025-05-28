from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

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

def register(request: HttpRequest):
    user = request.POST.get("username")
    password = request.POST.get("password")
    email = request.POST.get("email")

    user = User.objects.create_user(user, email, password)
    user.save()

    return redirect("/map/user/login")
