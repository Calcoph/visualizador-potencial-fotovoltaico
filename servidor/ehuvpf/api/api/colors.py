from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import permission_required

from ..utils.user import Permission

from ..models import Layer, Project, Color
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
    colors = request.POST.getlist("color")
    project = get_project(request)

    update_colors_impl(project, colors)

    return HttpResponse(colors) # TODO: This is not an appropiate response

def update_colors_impl(project: Project, colors: list[str]):
    colores_proyecto = list(Color.objects.filter(project=project))
    colores_proyecto.sort(key=lambda color: color.strength)
    for (strength, color) in enumerate(colors):
        # TODO: validate color
        if strength < len(colores_proyecto):
            # Edita un color existente
            color_existente = colores_proyecto[strength]
            color_existente.hex = color
            color_existente.save()
        else:
            # Añade un nuevo color
            new_color = Color(project=project, hex=color, strength=strength)
            new_color.save()
            # TODO: haz un color rule para cada capa para este color

    # Borra los colores con strength > len(colors) (no se ha enviado estos colores)
    i = len(colors)
    while i < len(colores_proyecto):
        colores_proyecto[i].delete()
        i += 1
