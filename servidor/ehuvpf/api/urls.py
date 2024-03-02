from django.urls import path

from . import views

urlpatterns = [
    path("getBuildings", views.get_buildings, name="getBuildings")
]
