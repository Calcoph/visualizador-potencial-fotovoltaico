from django.urls import include, path, re_path

from . import views, api

# /map/api/*
api_urls = [
    path("createProject", api.create_project, name="createProject"),

    path("getBuildings", api.get_buildings, name="getBuildings"),
    path("getPlaceholderBuildings", api.get_placeholder_buildings, name="getPlaceholderBuildings"),
    path("addBuilding", api.add_building, name="addBuilding"),

    path("getAttributes", api.get_attributes, name="getAttributes"),
    path("newAttribute", api.new_attribute, name="newAttribute"),

    path("editLayer", api.edit_layer, name="newAttribute"),

    path("selectProject", api.select_project, name="selectProject"),

    path("addLayer", api.add_layer, name="addLayer"),
    path("getLayers", api.get_layers, name="getLayers"),
]

# /map/*
urlpatterns = [
    path("api/", include(api_urls)),

    path("", views.index, name="index"),
    path("project-admin", views.project_admin, name="project-admin"),
    path("edit-layers", views.edit_layers, name="edit-layers"),
    path("edit-attributes", views.edit_attributes, name="edit-attributes"),
    path("edit-layer", views.edit_layer, name="edit-layer"),
    path("edit-colors", views.edit_colors, name="edit-colors"),
    path("add-layer", views.add_layer, name="edit-layers"),
    path("add-building", views.add_building, name="edit-layers"),
    re_path("project-list.html", views.project_list, name="login"),
    re_path("\w\.html", views.static_html, name="login"),
]
