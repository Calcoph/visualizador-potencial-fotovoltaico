from django.urls import path

from . import views

urlpatterns = [
    path("getBuildings", views.get_buildings, name="getBuildings"),
    path("getPlaceholderBuildings", views.get_placeholder_buildings, name="get_placeholder_buildings"),
    path("addBuilding", views.add_building, name="addBuilding"),
]
