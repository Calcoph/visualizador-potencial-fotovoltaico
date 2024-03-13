from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from .utils.testing import generate_placeholder_building

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
