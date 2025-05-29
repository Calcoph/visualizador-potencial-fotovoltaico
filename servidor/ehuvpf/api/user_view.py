from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.contrib import auth

def logout(request: HttpRequest):
    template = loader.get_template("user/logout.html")
    auth.logout(request)

    return HttpResponse(template.render({}, request))
