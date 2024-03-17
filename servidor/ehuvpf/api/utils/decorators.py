
from django.http import HttpRequest
from django.shortcuts import redirect

from .session_handler import SESSION_PROJECT_ID

def rendered_view(func):
    def view_wrapper(request: HttpRequest, *args, **kwargs):
        if request.session.has_key(SESSION_PROJECT_ID):
            return func(request, *args, **kwargs)
        else:
            response = redirect(f"/map/project-list.html")
            response.set_cookie("project-list-source", request.path, max_age=600)
            return response

    return view_wrapper

def api_view(func):
    def view_wrapper(request: HttpRequest, *args, **kwargs):
        return func(request, *args, **kwargs)

    return view_wrapper
