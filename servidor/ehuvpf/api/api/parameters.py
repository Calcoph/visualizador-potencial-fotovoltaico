from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import permission_required

from ..utils.errors import ApiError, ErrorKind

from ..utils.user import Permission

from ..models import Parameter, Project
from ..utils.session_handler import get_project
from ..utils.decorators import project_required_api

class AddParameterParams:
    def __init__(self, name: str, description: str, value: str) -> None:
        self.name = name
        self.description = description
        self.value = value

    def validate(request: HttpRequest) -> AddParameterParams | ApiError:
        endpoint = "add_parameter"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        try:
            # Required parameters
            param_name = "name"
            name = request.POST.get(param_name)
            if name == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            param_name = "description"
            description = request.POST.get(param_name)
            if description == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            param_name = "value"
            value = request.POST.get(param_name)
            if value == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())
        except:
            return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())

        return AddParameterParams(name, description, value)

@permission_required(Permission.ParameterAdd)
@project_required_api
def add_parameter(request: HttpRequest):
    project = get_project(request)

    parameters = AddParameterParams.validate(request)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        add_parameter_impl(parameters, project)
        return HttpResponse("Success")

def add_parameter_impl(parameters: AddParameterParams, project: Project):
    parameter = Parameter(
        project=project,
        name=parameters.name,
        description=parameters.description,
        value=parameters.value
    )
    parameter.save()

class EditParameterParams:
    def __init__(self, name: str, description: str, value: str, parameter: Parameter) -> None:
        self.name = name
        self.description = description
        self.value = value
        self.parameter = parameter

    def validate(request: HttpRequest, project: Project) -> EditParameterParams | ApiError:
        endpoint = "edit_parameter"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        try:
            # Required parameters
            param_name = "name"
            name = request.POST.get(param_name)
            if name == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            param_name = "description"
            description = request.POST.get(param_name)
            if description == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            param_name = "value"
            value = request.POST.get(param_name)
            if value == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            parameter_id_param_name = "id"
            id = request.POST.get(parameter_id_param_name)
            if id == None:
                return ApiError(endpoint, f'"{parameter_id_param_name}" is required', ErrorKind.bad_request())

            parameter = Parameter.objects.get(pk=id)
            if parameter == None:
                return ApiError(endpoint, f'"{parameter_id_param_name}" must be the id of an existing parameter', ErrorKind.bad_request())
        except:
            return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())

        # Integrity check
        if parameter.project.pk != project.pk:
            return ApiError(endpoint, f'"{parameter_id_param_name}" must be the id of a parameter of the selected project', ErrorKind.bad_request())

        return EditParameterParams(name, description, value, parameter)

@permission_required(Permission.ParameterEdit)
@project_required_api
def edit_parameter(request: HttpRequest):
    project = get_project(request)

    parameters = AddParameterParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_parameter_impl(parameters)
        return HttpResponse("Success")


def edit_parameter_impl(parameters: EditParameterParams):
    parameter = parameters.parameter
    parameter.name = parameters.name
    parameter.description = parameters.description
    parameter.value = parameters.value

    parameter.save()

def delete_parameter_validate(request: HttpRequest, project: Project) -> Parameter | ApiError:
    endpoint = "delete_parameter"

    # Method check
    method = "POST"
    if request.method != method:
        return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

    try:
        # Required parameters
        parameter_id_param_name = "id"
        id = request.POST.get(parameter_id_param_name)
        if id == None:
            return ApiError(endpoint, f'"{parameter_id_param_name}" is required', ErrorKind.bad_request())

        parameter = Parameter.objects.get(pk=id)
        if parameter == None:
            return ApiError(endpoint, f'"{parameter_id_param_name}" must be the id of an existing parameter', ErrorKind.bad_request())
    except:
        return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())

    # Integrity check
    if parameter.project.pk != project.pk:
        return ApiError(endpoint, f'"{parameter_id_param_name}" must be the id of a parameter of the selected project', ErrorKind.bad_request())

    return parameter

@permission_required(Permission.ParameterDelete)
@project_required_api
def delete_parameter(request: HttpRequest):
    project = get_project(request)

    parameter = delete_parameter_validate(request, project)
    if isinstance(parameter, ApiError):
        return parameter.to_response()
    else:
        parameter.delete()
        return HttpResponse("Success")
