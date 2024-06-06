from django.http import HttpRequest
from ...models import Project

SESSION_PROJECT_ID = "project_id"

def get_project(request: HttpRequest) -> Project | None:
    if request.session.has_key(SESSION_PROJECT_ID):
        id = request.session[SESSION_PROJECT_ID]
        return Project.objects.get(pk=id)
    else:
        return None

def set_project(request: HttpRequest, id):
    # TODO: Make sure that project_id is valid
    request.session[SESSION_PROJECT_ID] = id

def default_project_if_undefined(request: HttpRequest):
    if not request.session.has_key(SESSION_PROJECT_ID):
        request.session[SESSION_PROJECT_ID] = Project.objects.first().pk
