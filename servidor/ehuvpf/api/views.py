from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from .utils.testing import generate_placeholder_building
from .utils.esri_gjson import save_esri, convert_esri_to_geojson

RESOLUTION = 0.1

def get_buildings(request: HttpRequest):
    params = request.GET
    lat = params.get("lat")
    lon = params.get("lon")
    return HttpResponse(f"Has pedido los edificios de lat:{lat} lon:{lon}")

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
    params = request.POST

    prj = request.FILES["prj"]
    dbf = request.FILES["dbf"]
    shx = request.FILES["shx"]
    shp = request.FILES["shp"]
    layer_name = prj.name.split(".prj")[0]

    save_esri(prj, dbf, shx, shp, layer_name)
    # TODO: use esri_to_geojson instead and keep a qgis app open for longer
    convert_esri_to_geojson(layer_name, f"/var/lib/ehuvpf/ehuvpf-projects/0/{layer_name}.geojson")

    return HttpResponse("Successfully saved")
