from os import makedirs

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template import loader

from .utils.testing import generate_placeholder_building
from .utils.esri_gjson import save_esri, convert_esri_to_geojson
from .utils.decorators import project_required_api, project_required
from .utils.session_handler import get_project, set_project, default_project_if_undefined
from .models import Building, Layer, Project, Measure

from qgis.core import QgsApplication

import json

@project_required
def project_admin(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/project-admin.html")
    attributes = Measure.objects.filter(project=project)
    layers = Layer.objects.filter(project=project)
    context = {
        "project": project,
        "attributes": attributes,
        "layers": layers,
    }
    return HttpResponse(template.render(context, request))

@project_required
def edit_layers(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/edit-layers.html")
    layers = Layer.objects.filter(project=project)
    context = {
        "project": project,
        "layers": layers,
    }
    return HttpResponse(template.render(context, request))

@project_required
def edit_layer(request: HttpRequest):
    layer_id = request.GET["layer"]
    project = get_project(request)
    template = loader.get_template("map/edit-layer.html")

    layer = Layer.objects.get(pk=layer_id)
    attributes = Measure.objects.filter(project=project)
    default_measures = layer.default_measures.all()
    # TODO: hacer este fitro con un query en vez de manualmente
    default_measures_pks = list(map(lambda x: x.pk, default_measures))
    unused_measures = []
    for measure in attributes:
        if measure.pk not in default_measures_pks:
            unused_measures.append(measure)
    color_measure = layer.color_measure
    context = {
        "project": project,
        "layer": layer,
        "attributes": attributes,
        "default_measures": default_measures,
        "unused_measures": unused_measures,
        "color_measure": color_measure
    }

    return HttpResponse(template.render(context, request))

@project_required
def add_layer(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/add-layer.html")

    attributes = Measure.objects.filter(project=project)
    context = {
        "project": project,
        "attributes": attributes,
    }

    return HttpResponse(template.render(context, request))

@project_required
def edit_attributes(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/edit-attributes.html")
    attributes = Measure.objects.filter(project=project)
    context = {
        "attributes": attributes,
    }
    return HttpResponse(template.render(context, request))

@project_required
def add_building(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/add-building.html")
    layers = Layer.objects.filter(project=project)
    context = {
        "layers": layers,
    }
    return HttpResponse(template.render(context, request))

@project_required
def static_html(request: HttpRequest):
    file_name = request.path.split("/")[-1]
    template = loader.get_template(f"map/{file_name}")
    context = {
    }
    response = HttpResponse(template.render(context, request))
    # Al ser estáticas se les puede indicar que se guarden en el caché
    response.headers["Cache-Control"] = f"max-age={60*24*14}"
    return response

def project_list(request: HttpRequest):
    template = loader.get_template(f"map/project-list.html")
    current_project = get_project(request)
    projects = Project.objects.all()
    context = {
        "projects": projects,
        "current_project": current_project,
    }
    return HttpResponse(template.render(context, request))

def index(request: HttpRequest):
    default_project_if_undefined(request)

    template = loader.get_template(f"map/index.html")
    context = {
    }
    return HttpResponse(template.render(context, request))
