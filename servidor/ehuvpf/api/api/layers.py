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
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        layer_param_name = "layer"
        try:
            layer = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "name-pattern"
        try:
            name_pattern = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        attribute_param_name = "attribute"
        try:
            attributes = request.POST.getlist(attribute_param_name)
        except:
            return ApiError(endpoint, f'"{attribute_param_name}" is required', ErrorKind.BAD_REQUEST)
        color_attribute_param_name = "color-attribute"
        try:
            color_attribute = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        color_rule_param_name = "color_rule"
        try:
            color_rules = request.POST.getlist(color_rule_param_name)
        except:
            return ApiError(endpoint, f'"{color_rule_param_name}" is required', ErrorKind.BAD_REQUEST)

        new_color_rules = []
        for color_rule in color_rules:
            try:
                new_color_rule = float(color_rule.replace(",", "."))
            except:
                return ApiError(endpoint, f'"{color_rule_param_name}" must be a list of floats, got: {color_rule}', ErrorKind.BAD_REQUEST)
            new_color_rules.append(new_color_rule)

        try:
            layer = Layer.objects.get(pk=layer)
        except:
            return ApiError(endpoint, f'"{layer_param_name}" must be the id of an existing layer', ErrorKind.BAD_REQUEST)
        if layer.project.pk != project.pk:
            return ApiError(endpoint, f'"{layer_param_name}" must be the id of a layer of the selected project', ErrorKind.BAD_REQUEST)

        try:
            color_attribute = Measure.objects.get(pk=color_attribute)
        except:
            return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an existing attribute', ErrorKind.BAD_REQUEST)
        if color_attribute.project.pk != project.pk:
            return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)

        attribute_list = []
        for attribute_id in attributes:
            try:
                attribute = Measure.objects.get(pk=attribute_id)
            except:
                return ApiError(endpoint, f'"{attribute_id}" is not the id of an existing attribute', ErrorKind.BAD_REQUEST)
            if attribute.project.pk != project.pk:
                return ApiError(endpoint, f'"{attribute_id}" is not the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)
            attribute_list.append(attribute)

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

    # TODO: Asegurarse que name_pattern no es subset de otro patrón
    layer.name_pattern = params.name_pattern
    layer.color_measure = params.color_attribute

    layer.default_measures.set(params.attribute_list)

    layer.save()

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
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "layer-name"
        try:
            layer_name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "attributes"
        try:
            attributes = request.POST.getlist(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        color_attribute_param_name = "color-attribute"
        try:
            color_attribute = request.POST.get(color_attribute_param_name)
        except:
            return ApiError(endpoint, f'"{color_attribute_param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "name-pattern"
        try:
            name_pattern = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        try:
            color_attribute = Measure.objects.get(pk=color_attribute)
        except:
            return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an existing attribute', ErrorKind.BAD_REQUEST)
        if color_attribute.project.pk != project.pk:
            return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)

        attribute_list = []
        for attribute_id in attributes:
            try:
                attribute = Measure.objects.get(pk=attribute_id)
            except:
                return ApiError(endpoint, f'"{attribute_id}" is not the id of an existing attribute', ErrorKind.BAD_REQUEST)
            if attribute.project.pk != project.pk:
                return ApiError(endpoint, f'"{attribute_id}" is not the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)
            attribute_list.append(attribute)

        return AddLayerParams(layer_name, attribute_list, color_attribute, name_pattern)

@permission_required(Permission.LayerAdd)
@project_required_api
def add_layer(request: HttpRequest):
    project = get_project(request)

    parameters = AddLayerParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_layer_impl(project, parameters)
        return HttpResponse("Success")

def add_layer_impl(project: Project, params: AddLayerParams):
    # TODO: Asegurarse que name_pattern no es subset de otro patrón
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
