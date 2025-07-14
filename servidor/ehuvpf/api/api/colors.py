from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import permission_required

from ..utils.user import Permission
from ..utils.errors import ApiError

from ..models import ColorRule, Layer, Project, Color
from ..utils.session_handler import get_project
from ..utils.decorators import project_required_api

@project_required_api
def get_colors(request: HttpRequest):
    project = get_project(request)

    resp = get_colors_impl(project)

    return JsonResponse(resp)

def get_colors_impl(project: Project):
    colors = list(Color.objects.filter(project=project))
    colors.sort(key=lambda color: color.strength)
    json_colors = []
    for color in colors:
        json_colors.append(color.hex)

    minimums = {}
    layers = Layer.objects.filter(project=project)
    for layer in layers:
        color_rules = list(layer.color_rules.all())
        color_rules.sort(key=lambda color_rule: color_rule.color.strength)
        layer_minimums = list(map(lambda color_rule: color_rule.minimum, color_rules))
        minimums[str(layer.pk)] = layer_minimums

    resp = {
        "colors": json_colors,
        "minimums": minimums
    }

    return resp

@permission_required(Permission.ColorEdit)
@project_required_api
def update_colors(request: HttpRequest):
    endpoint = "update_colors"

    colors = request.POST.getlist("color")
    project = get_project(request)

    # validate color format
    for color in colors:
        if len(color) != 7: # 7 = len("#RrGgBb")
            return ApiError(endpoint, f'Color "{color}" is invalid. It must be of the pattern "#RrGgBb"').to_response()

        if color[0] != "#":
            return ApiError(endpoint, f'Color "{color}" is invalid. It must be of the pattern "#RrGgBb"').to_response()

        for hex in color[1:]:
            if hex.lower() not in ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']:
                return ApiError(endpoint, f'Color "{color}" is invalid. It must be of the pattern "#RrGgBb" where "RrGgBb" are hexadecimal characters').to_response()

    update_colors_impl(project, colors)

    return HttpResponse("Success")

def update_colors_impl(project: Project, colors: list[str]):
    colores_proyecto = list(Color.objects.filter(project=project))
    colores_proyecto.sort(key=lambda color: color.strength)
    for (strength, color) in enumerate(colors):
        if strength < len(colores_proyecto):
            # Edita un color existente
            color_existente = colores_proyecto[strength]
            color_existente.hex = color
            color_existente.save()
        else:
            # Añade un nuevo color
            new_color = Color(project=project, hex=color, strength=strength)
            new_color.save()

            for layer in Layer.objects.filter(project=project):
                new_color_rule = ColorRule(color=new_color, minimum=0.0)
                new_color_rule.save()
                layer.color_rules.add(new_color_rule)

    # Borra los colores con strength > len(colors) (no se ha enviado estos colores)
    i = len(colors)
    while i < len(colores_proyecto):
        colores_proyecto[i].delete()
        i += 1
