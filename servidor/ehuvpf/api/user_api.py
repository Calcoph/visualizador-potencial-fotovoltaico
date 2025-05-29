from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from .models import AllowedEmail

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

    try:
        allowed_email = AllowedEmail.objects.get(email=email)
    except Exception:
        return redirect("/map/error-page?msg=%s" % _("Esta dirección de email no está autorizada para crear una cuenta. Contacta con la administración de la página si crees que esto es un error."))

    if User.objects.filter(username=user).exists():
        return redirect("/map/error-page?msg=%s" % _("El nombre de usuario o email elegido ya existe"))

    if User.objects.filter(email=email).exists():
        return redirect("/map/error-page?msg=%s" %_("El nombre de usuario o email elegido ya existe"))

    allowed_email.delete()

    user = User.objects.create_user(user, email, password)
    user.save()

    return redirect("login")
