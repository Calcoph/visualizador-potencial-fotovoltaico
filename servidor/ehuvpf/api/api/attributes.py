from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import permission_required

from .utils.errors import ApiError, ErrorKind

from .utils.user import Permission

from ..models import Measure, Project
from .utils.session_handler import get_project
from .utils.decorators import project_required_api

# @permission_required(Permission.MeasureView) # Commented out because this should be accessible by anyone
@project_required_api
def get_attributes(request: HttpRequest):
    project = get_project(request)

    attributes = get_attributes_impl(project)

    return JsonResponse(attributes)

def get_attributes_impl(project: Project):
    measures = Measure.objects.filter(project=project)
    measure_list = []
    for measure in measures:
        measure_list.append({
            "name": measure.name,
            "display_name": measure.display_name,
        })

    attributes = {
        "available_attributes": measure_list
    }

    return attributes

class AddAttributeParams:
    def __init__(self, name: str, display_name: str, description: str, unit: str) -> None:
        self.name = name
        self.display_name = display_name
        self.description = description
        self.unit = unit

    def validate(request: HttpRequest) -> AddAttributeParams | ApiError:
        endpoint = "add_attribute"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "name"
        try:
            name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "display_name"
        try:
            display_name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "description"
        try:
            description = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "unit"
        try:
            unit = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        return AddAttributeParams(name, display_name, description, unit)

@permission_required(Permission.MeasureAdd)
@project_required_api
def add_attribute(request: HttpRequest):
    project = get_project(request)

    parameters = AddAttributeParams.validate(request)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        add_attribute_impl(project, parameters)
        return HttpResponse("Success")

def add_attribute_impl(project: Project, parameters: AddAttributeParams):
    new_measure = Measure(
        project=project,
        name=parameters.name,
        display_name=parameters.display_name,
        description=parameters.description,
        unit=parameters.unit
    )
    new_measure.save()

class EditAttributeParams:
    def __init__(self, name: str, display_name: str, description: str, unit: str, attribute: Measure) -> None:
        self.name = name
        self.display_name = display_name
        self.description = description
        self.unit = unit
        self.attribute = attribute

    def validate(request: HttpRequest, project: Project) -> EditAttributeParams | ApiError:
        endpoint = "edit_attribute"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "name"
        try:
            name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "display_name"
        try:
            display_name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "description"
        try:
            description = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "unit"
        try:
            unit = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        attribute_id_param_name = "id"
        try:
            id = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        try:
            attribute = Measure.objects.get(pk=id)
        except:
            return ApiError(endpoint, f'"{attribute_id_param_name}" must be the id of an existing attribute', ErrorKind.BAD_REQUEST)

        # Integrity check
        if attribute.project.pk != project.pk:
            return ApiError(endpoint, f'"{attribute_id_param_name}" must be the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)

        return EditAttributeParams(name, display_name, description, unit, attribute)

@permission_required(Permission.MeasureEdit)
@project_required_api
def edit_attribute(request: HttpRequest):
    project = get_project(request)

    parameters = EditAttributeParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_attribute_impl(parameters)
        return HttpResponse("Success")

def edit_attribute_impl(parameters: EditAttributeParams):
    editing_attribute = parameters.attribute
    editing_attribute.name = parameters.name
    editing_attribute.display_name = parameters.display_name
    editing_attribute.description = parameters.description
    editing_attribute.unit = parameters.unit

    editing_attribute.save()
