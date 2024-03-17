from django.urls import include, path, re_path

from . import views

# /map/api/*
api_urls = [
    path("getBuildings", views.get_buildings, name="getBuildings"),
    path("getPlaceholderBuildings", views.get_placeholder_buildings, name="getPlaceholderBuildings"),
    path("getAttributes", views.get_attributes, name="getAttributes"),
    path("addBuilding", views.add_building, name="addBuilding"),
    path("newAttribute", views.new_attribute, name="newAttribute"),
    path("selectProject", views.select_project, name="selectProject"),
]

# /map/*
urlpatterns = [
    path("api/", include(api_urls)),

    path("", views.index, name="index"),
    path("project-admin", views.project_admin, name="project-admin"),
    re_path("project-list.html", views.project_list, name="login"),
    re_path("\w\.html", views.static_html, name="login"),
]
