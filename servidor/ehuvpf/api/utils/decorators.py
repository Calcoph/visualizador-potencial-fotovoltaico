
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .session_handler import SESSION_PROJECT_ID

def project_required(func):
    def view_wrapper(request: HttpRequest, *args, **kwargs):
        if request.session.has_key(SESSION_PROJECT_ID):
            return func(request, *args, **kwargs)
        else:
            response = redirect(f"/map/project-list.html")
            response.set_cookie("project-list-source", request.path, max_age=600)
            return response

    return view_wrapper

def project_required_api(func):
    def view_wrapper(request: HttpRequest, *args, **kwargs):
        if request.session.has_key(SESSION_PROJECT_ID):
            return func(request, *args, **kwargs)
        else:
            response = HttpResponse()
            response.status_code = 400
            return response

    return view_wrapper
