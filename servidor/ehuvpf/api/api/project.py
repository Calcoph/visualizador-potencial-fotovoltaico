from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import permission_required

from ..utils.session_handler import set_project

from ..utils.errors import ApiError, ErrorKind

from ..utils.user import Permission

from ..models import Project
from ..utils.session_handler import get_project
from ..utils.decorators import project_required_api

@permission_required(Permission.ProjectAdd)
def create_project(request: HttpRequest):
    name = request.POST.get("name")

    create_project_impl(name)

    return HttpResponse("Success")

def create_project_impl(name: str):
    project = Project(name=name)
    project.save()

class EditPreprocessInfoParams:# TODO: Delete this class
    def __init__(self, link: str, name: str, version: str) -> None:
        self.link = link
        self.name = name
        self.version = version

    def validate(request: HttpRequest) -> EditPreprocessInfoParams | ApiError:
        endpoint = "edit_preprocess_info"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        # Required parameters
        param_name = "preprocess_link"
        try:
            preprocess_link = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())
        param_name = "preprocess_name"
        try:
            preprocess_name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())
        param_name = "preprocess_version"
        try:
            preprocess_version = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

        return EditPreprocessInfoParams(preprocess_link, preprocess_name, preprocess_version)

@permission_required(Permission.PreprocessingInfoEdit)
@project_required_api
def edit_preprocess_info(request: HttpRequest):
    project = get_project(request)

    parameters = EditPreprocessInfoParams.validate(request)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_preprocess_info_impl(project, parameters)
        return HttpResponse("Success")

def edit_preprocess_info_impl(project: Project, parameters: EditPreprocessInfoParams):
    project.preprocess_program_link = parameters.link
    project.preprocess_program_name = parameters.name
    project.preprocess_program_version = parameters.version
    project.save()

class EditDataSourceParams:# TODO: Delete this class
    def __init__(self, data_source: str) -> None:
        self.data_source = data_source

    def validate(request: HttpRequest, project: Project) -> EditDataSourceParams | ApiError:
        endpoint = "edit_data_source"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        # Required parameters
        param_name = "data_source"
        try:
            data_source = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

        return EditDataSourceParams(data_source)

@permission_required(Permission.DataSourceEdit)
@project_required_api
def edit_data_source(request: HttpRequest):
    project = get_project(request)

    parameters = EditDataSourceParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_data_source_impl(project, parameters)
        return HttpResponse("Success")

def edit_data_source_impl(project: Project, parameters: EditDataSourceParams):
    project.data_source = parameters.data_source
    project.save()

# @permission_required(Permission.ProjectView) # Commented out because this should be accessible by anyone
def select_project(request: HttpRequest):
    project_id = request.POST.get("project_id")
    selected = set_project(request, project_id)

    if selected:
        response = HttpResponse("Success")
    else:
        response = ApiError("select_project", "Unexisting project", ErrorKind.unprocessable())

    return response
