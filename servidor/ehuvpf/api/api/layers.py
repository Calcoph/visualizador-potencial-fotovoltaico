from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import permission_required

from ..utils.errors import ApiError, ErrorKind

from ..utils.user import Permission

from ..models import Layer, Measure, Project, ColorRule
from ..utils.session_handler import get_project
from ..utils.decorators import project_required_api

class EditLayerParams:
    def __init__(self, layer: Layer, name_pattern: str, attribute_list: list[Measure], color_attribute: list[Measure], new_color_rules: list[float]) -> None:
        self.layer = layer
        self.name_pattern = name_pattern
        self.attribute_list = attribute_list
        self.color_attribute = color_attribute
        self.new_color_rules = new_color_rules

    def validate(request: HttpRequest, project: Project) -> EditLayerParams | ApiError:
        endpoint = "edit_layer"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        try:
            # Required parameters
            layer_param_name = "id"
            layer = request.POST.get(layer_param_name)
            if layer == None:
                return ApiError(endpoint, f'"{layer_param_name}" is required', ErrorKind.bad_request())

            param_name = "name-pattern"
            name_pattern = request.POST.get(param_name)
            if name_pattern == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            attribute_param_name = "attribute"
            attributes = request.POST.getlist(attribute_param_name)
            if attributes == None:
                return ApiError(endpoint, f'"{attribute_param_name}" is required', ErrorKind.bad_request())

            color_attribute_param_name = "color-attribute"
            color_attribute = request.POST.get(color_attribute_param_name)
            if color_attribute == None:
                return ApiError(endpoint, f'"{color_attribute_param_name}" is required', ErrorKind.bad_request())

            color_rule_param_name = "color_rule"
            color_rules = request.POST.getlist(color_rule_param_name)
            if color_rules == None:
                return ApiError(endpoint, f'"{color_rule_param_name}" is required', ErrorKind.bad_request())

            new_color_rules = []
            for color_rule in color_rules:
                new_color_rule = float(color_rule.replace(",", "."))
                if new_color_rule == None:
                    return ApiError(endpoint, f'"{color_rule_param_name}" must be a list of floats, got: {color_rule}', ErrorKind.bad_request())
                new_color_rules.append(new_color_rule)

            layer = Layer.objects.get(pk=layer)
            if layer == None:
                return ApiError(endpoint, f'"{layer_param_name}" must be the id of an existing layer', ErrorKind.bad_request())
            if layer.project.pk != project.pk:
                return ApiError(endpoint, f'"{layer_param_name}" must be the id of a layer of the selected project', ErrorKind.bad_request())

            color_attribute = Measure.objects.get(pk=color_attribute)
            if color_attribute == None:
                return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an existing attribute', ErrorKind.bad_request())
            if color_attribute.project.pk != project.pk:
                return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an attribute of the selected project', ErrorKind.bad_request())

            attribute_list = []
            for attribute_id in attributes:
                attribute = Measure.objects.get(pk=attribute_id)
                if attribute == None:
                    return ApiError(endpoint, f'"{attribute_id}" is not the id of an existing attribute', ErrorKind.bad_request())
                if attribute.project.pk != project.pk:
                    return ApiError(endpoint, f'"{attribute_id}" is not the id of an attribute of the selected project', ErrorKind.bad_request())
                attribute_list.append(attribute)

            layers = Layer.objects.filter(project=project)
            for layer in layers:
                if layer.pk == layer:
                    continue # Don't check pattern conflicts with self
                if name_pattern in layer.name_pattern or layer.name_pattern in name_pattern:
                    return ApiError(endpoint, f'"{name_pattern}" conflicts with pattern "{layer.name_pattern}" of layer "{layer.name}"', ErrorKind.bad_request())
        except:
            return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())
        return EditLayerParams(layer, name_pattern, attribute_list, color_attribute, new_color_rules)

@permission_required(Permission.LayerEdit)
@project_required_api
def edit_layer(request: HttpRequest):
    project = get_project(request)

    parameters = EditLayerParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_layer_impl(parameters)
        return HttpResponse("Success")


def edit_layer_impl(params: EditLayerParams):
    layer = params.layer
    for rule in layer.color_rules.all():
        rule: ColorRule
        new_minimum = params.new_color_rules[rule.color.strength]
        rule.minimum = new_minimum
        rule.save()

    layer.name_pattern = params.name_pattern
    layer.color_measure = params.color_attribute

    layer.default_measures.set(params.attribute_list)

    layer.save()

class DeleteLayerParams:
    def __init__(self, layer: Layer) -> None:
        self.layer = layer

    def validate(request: HttpRequest, project: Project) -> DeleteLayerParams | ApiError:
        endpoint = "delete_layer"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        try:
            # Required parameters
            param_name = "id"
            id = request.POST.get(param_name)
            if id == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            layer = Layer.objects.get(pk=id)
            if layer == None:
                return ApiError(endpoint, f'"{param_name}" must be the id of an existing layer', ErrorKind.bad_request())
            if layer.project.pk != project.pk:
                return ApiError(endpoint, f'"{param_name}" must be the id of a layer of the selected project', ErrorKind.bad_request())
        except:
            return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())

        return DeleteLayerParams(layer)

@permission_required(Permission.LayerDelete)
@project_required_api
def delete_layer(request: HttpRequest):
    project = get_project(request)

    parameters = DeleteLayerParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        delete_layer_impl(parameters)
        return HttpResponse("Success")

def delete_layer_impl(params: DeleteLayerParams):
    layer = params.layer
    # Delete all its associated color rules, since they are layer dependant
    for rule in layer.color_rules.all():
        rule.delete()

    layer.delete()

class AddLayerParams:# TODO: Delete this class
    def __init__(self, layer_name: str, attribute_list: list[Measure], color_attribute: Measure, name_pattern: str) -> None:
        self.layer_name = layer_name
        self.attribute_list = attribute_list
        self.color_attribute = color_attribute
        self.name_pattern = name_pattern

    def validate(request: HttpRequest, project: Project) -> AddLayerParams | ApiError:
        # TODO Make sure that no other layer exists with this name on this project
        endpoint = "add_layer"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        try:
            # Required parameters
            param_name = "layer-name"
            layer_name = request.POST.get(param_name)
            if layer_name == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            param_name = "attributes"
            attributes = request.POST.getlist(param_name)
            if attributes == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            color_attribute_param_name = "color-attribute"
            color_attribute = request.POST.get(color_attribute_param_name)
            if color_attribute == None:
                return ApiError(endpoint, f'"{color_attribute_param_name}" is required', ErrorKind.bad_request())

            param_name = "name-pattern"
            name_pattern = request.POST.get(param_name)
            if name_pattern == None:
                return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.bad_request())

            color_attribute = Measure.objects.get(pk=color_attribute)
            if color_attribute == None:
                return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an existing attribute', ErrorKind.bad_request())
            if color_attribute.project.pk != project.pk:
                return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an attribute of the selected project', ErrorKind.bad_request())

            attribute_list = []
            for attribute_id in attributes:
                attribute = Measure.objects.get(pk=attribute_id)
                if attribute == None:
                    return ApiError(endpoint, f'"{attribute_id}" is not the id of an existing attribute', ErrorKind.bad_request())
                if attribute.project.pk != project.pk:
                    return ApiError(endpoint, f'"{attribute_id}" is not the id of an attribute of the selected project', ErrorKind.bad_request())
                attribute_list.append(attribute)

            layers = Layer.objects.filter(project=project)
            for layer in layers:
                if name_pattern in layer.name_pattern or layer.name_pattern in name_pattern:
                    return ApiError(endpoint, f'"{name_pattern}" conflicts with pattern "{layer.name_pattern}" of layer "{layer.name}"', ErrorKind.bad_request())
                if layer_name == layer.name:
                    return ApiError(endpoint, f'Layer "{layer.name}" already exists', ErrorKind.bad_request())
        except:
            return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())

        return AddLayerParams(layer_name, attribute_list, color_attribute, name_pattern)

@permission_required(Permission.LayerAdd)
@project_required_api
def add_layer(request: HttpRequest):
    project = get_project(request)

    parameters = AddLayerParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        add_layer_impl(project, parameters)
        return HttpResponse("Success")

def add_layer_impl(project: Project, params: AddLayerParams):
    # TODO: Hacer un color rule por cada color del proyecto
    new_layer = Layer(project=project, color_measure=params.color_attribute, name=params.layer_name, name_pattern=params.name_pattern)
    new_layer.save()
    new_layer.default_measures.set(params.attribute_list)

# @permission_required(Permission.LayerView) # Commented out because this should be accessible by anyone
@project_required_api
def get_layers(request: HttpRequest):
    project = get_project(request)

    resp = get_layers_impl(project)

    return JsonResponse(resp)

def get_layers_impl(project: Project):
    layers = Layer.objects.filter(project=project)
    json_layers = []
    for layer in layers:
        measures = []
        for measure in layer.default_measures.all():
            measures.append({
                "name": measure.name,
                "display_name": measure.display_name
            })
        json_layers.append({
            "name": layer.name,
            "measures": measures,
            "color_measure": layer.color_measure.name,
            "id": layer.pk
        })

    resp = {
        "layers": json_layers
    }

    return resp
