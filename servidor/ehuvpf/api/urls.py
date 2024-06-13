from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views

from .api import attributes as api_attributes, buildings as api_buildings, colors as api_colors, layers as api_layers, parameters as api_parameters, project as api_project

from . import views, user_view, user_api

# /map/user/api/*
user_api_urls = [
    path("login", user_api.login, name="apiLogin"),
    path("register", user_api.register, name="apiRegister")
]

# /map/user/*
user_urls = [
    path("api/", include(user_api_urls)),

    path("login", auth_views.LoginView.as_view(template_name="user/login.html"), name="login"),
    path("logout", user_view.logout, name="logout"),
    path("register", user_view.register, name="register")
]

# /map/api/*
api_urls = [
    path("createProject", api_project.create_project, name="createProject"),

    path("getBuildings", api_buildings.get_buildings, name="getBuildings"),
    path("getPlaceholderBuildings", api_buildings.get_placeholder_buildings, name="getPlaceholderBuildings"),
    path("addBuilding", api_buildings.add_building, name="addBuilding"),

    path("getAttributes", api_attributes.get_attributes, name="getAttributes"),
    path("addAttribute", api_attributes.add_attribute, name="newAttribute"),
    path("editAttribute", api_attributes.edit_attribute, name="editAttribute"),
    path("deleteAttribute", api_attributes.delete_attribute, name="deleteAttribute"),

    path("addParameter", api_parameters.add_parameter, name="newParameter"),
    path("editParameter", api_parameters.edit_parameter, name="editParameter"),

    path("editPreprocessInfo", api_project.edit_preprocess_info, name="editPreprocessInfo"),
    path("editDataSource", api_project.edit_data_source, name="editDataSource"),

    path("selectProject", api_project.select_project, name="selectProject"),

    path("getLayers", api_layers.get_layers, name="getLayers"),
    path("addLayer", api_layers.add_layer, name="addLayer"),
    path("editLayer", api_layers.edit_layer, name="newAttribute"),
    path("deleteLayer", api_layers.delete_layer, name="deleteLayer"),

    path("getColors", api_colors.get_colors, name="getColors"),
    path("updateColors", api_colors.update_colors, name="updateColors")
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
    path("project-list", views.project_list, name="project-list"),
    path("details", views.details, name="details"),
    path("index", views.index, name="index"),
    path("index.html", views.index, name="index"),
    re_path("\w\.html", views.static_html, name="static"),
]
