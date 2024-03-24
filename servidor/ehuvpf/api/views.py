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


RESOLUTION = 0.1
PROJECT_PATH = "/var/lib/ehuvpf/ehuvpf-projects"

@project_required_api
def get_buildings(request: HttpRequest):
    params = request.GET
    layer_id = params.get("layer")
    lat = params.get("lat")
    lon = params.get("lon")
    # TODO: Make sure "layer" is of this project
    project = get_project(request)
    layer = Layer.objects.get(pk=layer_id)

    buildings = Building.objects.filter(layer=layer, lat=lat, lon=lon)
    json_buildings = []
    for building in buildings:
        with open(building.path, "r") as f:
            building = json.load(f)
            json_buildings.append(building)

    resp = {
        "layer": layer_id,
        "buildings": json_buildings
    }

    return JsonResponse(resp)

@project_required_api
def get_placeholder_buildings(request: HttpRequest):
    params = request.GET
    lat = int(params.get("lat")) * RESOLUTION
    lon = int(params.get("lon")) * RESOLUTION

    buildings = []
    STEPS = 10
    for x in range(0, STEPS):
        for y in range(0, STEPS):
            t_lat = lat + (x / STEPS) * RESOLUTION
            t_lon = lon + (y / STEPS) * RESOLUTION
            buildings.append(generate_placeholder_building(t_lat, t_lon))

    json_buildings = {
        "buildings": buildings
    }

    return JsonResponse(json_buildings)

@project_required_api
def get_attributes(request: HttpRequest):
    project = get_project(request)
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

    return JsonResponse(attributes)

@project_required_api
def add_building_api(request: HttpRequest):
    prj = request.FILES["prj"]
    dbf = request.FILES["dbf"]
    shx = request.FILES["shx"]
    shp = request.FILES["shp"]
    layer_id = request.POST.get("layer")
    building_name = prj.name.split(".prj")[0]
    project = get_project(request)
    layer = Layer.objects.get(pk=layer_id)

    save_esri(prj, dbf, shx, shp, building_name)
    path = f"{PROJECT_PATH}/{project.pk}/{layer.name}"
    makedirs(path, exist_ok=True)
    path += f"/{building_name}.geojson"
    (output_path, lat, lon) = convert_esri_to_geojson(building_name, path)

    # Update database
    building = Building(layer=layer, path=output_path, lat=lat, lon=lon)
    building.save()

    return HttpResponse("Successfully saved")

@project_required_api
def new_attribute(request: HttpRequest):
    new_name = request.POST["name"]
    display_name = request.POST["display_name"]
    project = get_project(request)

    new_measure = Measure(project=project, name=new_name, display_name=display_name)
    new_measure.save()

    return HttpResponse("Success")

@project_required_api
def add_attribute(request: HttpRequest):
    layer_id = request.POST["layer"]
    attribute_id = request.POST["attribute"]

    layer = Layer.objects.get(pk=layer_id)
    attribute = Measure.objects.get(pk=attribute_id)

    # TODO: Validation
    layer.default_measures.add(attribute)

    return HttpResponse("Success")

@project_required_api
def hide_attribute(request: HttpRequest):
    layer_id = request.POST["layer"]
    attribute_id = request.POST["attribute"]

    layer = Layer.objects.get(pk=layer_id)
    attribute = Measure.objects.get(pk=attribute_id)

    # TODO: Validation
    layer.default_measures.remove(attribute)

    return HttpResponse("Success")

@project_required_api
def change_color_attribute(request: HttpRequest):
    layer_id = request.POST["layer"]
    color_attribute_id = request.POST["color_attribute"]

    layer = Layer.objects.get(pk=layer_id)
    color_attribute = Measure.objects.get(pk=color_attribute_id)
    # TODO: Validation
    layer.color_measure = color_attribute
    layer.save()

    return HttpResponse("Success")

@project_required_api
def add_layer_api(request: HttpRequest):
    # TODO: add validation
    # TODO Make sure that no other layer exists with this name on this project
    layer_name = request.POST["layer-name"]
    attributes = request.POST["attributes"]
    color_measure = request.POST["color-attribute"]
    project = get_project(request)

    measures = []
    for attribute in attributes:
        selected_measure = Measure.objects.get(pk=attribute)
        measures.append(selected_measure)

    color_measure = Measure.objects.get(pk=color_measure)

    new_layer = Layer(project=project, color_measure=color_measure, name=layer_name)
    new_layer.save()
    new_layer.default_measures.set(measures)

    return HttpResponse("Success")

@project_required_api
def get_layers(request: HttpRequest):
    project = get_project(request)

    layers = Layer.objects.filter(project=project)
    json_layers = []
    for layer in layers:
        json_layers.append({
            "name": layer.name,
            "id": layer.pk
        })

    resp = {
        "layers": json_layers
    }
    return JsonResponse(resp)

def select_project(request: HttpRequest):
    project_id = request.POST["project_id"]
    set_project(request, project_id)

    return HttpResponse("Success")

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
