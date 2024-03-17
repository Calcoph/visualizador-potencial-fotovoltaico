from django.urls import path, re_path

from . import views

urlpatterns = [
    # /map/api/*
    path("api/getBuildings", views.get_buildings, name="getBuildings"),
    path("api/getPlaceholderBuildings", views.get_placeholder_buildings, name="getPlaceholderBuildings"),
    path("api/addBuilding", views.add_building, name="addBuilding"),
    path("api/newAttribute", views.new_attribute, name="newAttribute"),
    # /map/*
    path("", views.index, name="index"),
    path("project-admin", views.project_admin, name="project-admin"),
    re_path("\w\.html", views.static_html, name="login"),
]
