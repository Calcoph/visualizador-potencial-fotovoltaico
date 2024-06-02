from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views

from . import views, api, user_view, user_api

# /map/user/api/*
user_api_urls = [
    path("login", user_api.login, name="apiLogin"),
    path("register", user_api.register, name="apiRegister")
]

# /map/user/*
user_urls = [
    path("api/", include(user_api_urls)),

    path("login", auth_views.LoginView.as_view(template_name="map/login.html"), name="login"),
    path("register", user_view.register, name="register")
]

# /map/api/*
api_urls = [
    path("createProject", api.create_project, name="createProject"),

    path("getBuildings", api.get_buildings, name="getBuildings"),
    path("getPlaceholderBuildings", api.get_placeholder_buildings, name="getPlaceholderBuildings"),
    path("addBuilding", api.add_building, name="addBuilding"),

    path("getAttributes", api.get_attributes, name="getAttributes"),
    path("addAttribute", api.add_attribute, name="newAttribute"),
    path("editAttribute", api.edit_attribute, name="editAttribute"),

    path("addParameter", api.add_parameter, name="newParameter"),
    path("editParameter", api.edit_parameter, name="editParameter"),

    path("editLayer", api.edit_layer, name="newAttribute"),

    path("selectProject", api.select_project, name="selectProject"),

    path("addLayer", api.add_layer, name="addLayer"),
    path("getLayers", api.get_layers, name="getLayers"),

    path("getColors", api.get_colors, name="getColors"),
    path("updateColors", api.update_colors, name="updateColors")
]

# /map/*
urlpatterns = [
    path("api/", include(api_urls)),
    path("user/", include(user_urls)),

    path("", views.index, name="index"),
    path("project-admin", views.project_admin, name="project-admin"),
    path("add-attribute", views.add_attribute, name="add-attribute"),
    path("edit-attribute", views.edit_attribute, name="edit-attribute"),
    path("add-parameter", views.add_parameter, name="add-parameter"),
    path("edit-parameter", views.edit_parameter, name="edit-parameter"),
    path("edit-layer", views.edit_layer, name="edit-layer"),
    path("edit-colors", views.edit_colors, name="edit-colors"),
    path("edit-project-details", views.edit_project_details, name="edit-project-details"),
    path("add-layer", views.add_layer, name="add-layer"),
    path("add-building", views.add_building, name="add-building"),
    path("project-list.html", views.project_list, name="project-list"),
    path("details", views.details, name="details"),
    path("index", views.index, name="index"),
    path("index.html", views.index, name="index"),
    re_path("\w\.html", views.static_html, name="static"),
]
