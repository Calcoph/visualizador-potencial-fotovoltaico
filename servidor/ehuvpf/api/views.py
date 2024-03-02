from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
def get_buildings(request: HttpRequest):
    params = request.GET
    lat = params.get("lat")
    lon = params.get("lon")
    return HttpResponse(f"Has pedido los edificios de lat:{lat} lon:{lon}")
