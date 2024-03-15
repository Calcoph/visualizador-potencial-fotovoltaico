from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from .utils.testing import generate_placeholder_building
from .utils.esri_gjson import save_esri, convert_esri_to_geojson
from .models import Building

from qgis.core import QgsApplication

import json

RESOLUTION = 0.1
PROJECT_PATH = "/var/lib/ehuvpf/ehuvpf-projects/0/"

def get_buildings(request: HttpRequest):
    params = request.GET
    lat = params.get("lat")
    lon = params.get("lon")

    buildings = Building.objects.filter(lat=lat, lon=lon)
    json_buildings = []
    for building in buildings:
        with open(building.path, "r") as f:
            building = json.load(f)
            json_buildings.append(building)

    resp = {
        "buildings": json_buildings
    }

    return JsonResponse(resp)

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

def add_building(request: HttpRequest):
    prj = request.FILES["prj"]
    dbf = request.FILES["dbf"]
    shx = request.FILES["shx"]
    shp = request.FILES["shp"]
    layer_name = prj.name.split(".prj")[0]

    save_esri(prj, dbf, shx, shp, layer_name)
    convert_esri_to_geojson(layer_name, f"{PROJECT_PATH}{layer_name}.geojson")

    return HttpResponse("Successfully saved")
