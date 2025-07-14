from os import makedirs

from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required

from .utils.decorators import project_required
from .utils.session_handler import get_project, default_project_if_undefined
from .utils.user import Permission
from .utils.errors import reponse_404
from .models import Color, Layer, Parameter, Project, Measure, ColorRule

@permission_required(Permission.AdminEditProject)
@project_required
def project_admin(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/project-admin.html")

    context = project_admin_impl(project)

    return HttpResponse(template.render(context, request))

def project_admin_impl(project: Project):
    attributes = Measure.objects.filter(project=project)
    layers = Layer.objects.filter(project=project)
    colors = list(Color.objects.filter(project=project))
    colors.sort(key=lambda color: color.strength)
    context = {
        "project": project,
        "attributes": attributes,
        "layers": layers,
        "colors": colors
    }

    return context

@permission_required(Permission.LayerEdit)
@project_required
def edit_layer(request: HttpRequest):
    layer_id = request.GET.get("layer")
    layer = Layer.objects.get(pk=layer_id)
    project = get_project(request)

    template = loader.get_template("map/edit-layer.html")
    context = edit_layer_impl(project, layer)

    return HttpResponse(template.render(context, request))

def edit_layer_impl(project: Project, layer: Layer) -> dict[str]:
    attributes = Measure.objects.filter(project=project)
    default_measures = layer.default_measures.all()
    default_measures_pks = list(map(lambda x: x.pk, default_measures))
    unused_measures = []
    for measure in attributes:
        if measure.pk not in default_measures_pks:
            unused_measures.append(measure)
    color_measure = layer.color_measure

    color_rules = list(layer.color_rules.all())

    context = {
        "project": project,
        "layer": layer,
        "attributes": attributes,
        "default_measures": default_measures,
        "unused_measures": unused_measures,
        "color_measure": color_measure,
        "color_rules": color_rules
    }

    return context

@permission_required(Permission.ColorEdit)
@project_required
def edit_colors(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/edit-colors.html")

    colors = list(Color.objects.filter(project=project))
    colors.sort(key=lambda color: color.strength)
    context = {
        "project": project,
        "colors": colors
    }

    return HttpResponse(template.render(context, request))

@permission_required(Permission.LayerAdd)
@project_required
def add_layer(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/add-layer.html")

    attributes = Measure.objects.filter(project=project)
    context = {
        "project": project,
        "attributes": attributes,
    }

    return HttpResponse(template.render(context, request))

@permission_required(Permission.MeasureAdd)
@project_required
def add_attribute(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/add-attribute.html")
    attributes = Measure.objects.filter(project=project)
    context = {
        "project": project,
        "attributes": attributes,
    }
    return HttpResponse(template.render(context, request))

@permission_required(Permission.MeasureEdit)
@project_required
def edit_attribute(request: HttpRequest):
    attribute_id = request.GET.get("id")
    attribute = Measure.objects.get(pk=attribute_id)
    project = get_project(request)
    template = loader.get_template("map/edit-attribute.html")
    context = {
        "attribute": attribute,
    }
    return HttpResponse(template.render(context, request))

@permission_required(Permission.ParameterAdd)
@project_required
def add_parameter(request: HttpRequest):
    project = get_project(request)
    template = loader.get_template("map/add-parameter.html")
    parameters = Parameter.objects.filter(project=project)
    context = {
        "project": project,
        "parameters": parameters,
    }
    return HttpResponse(template.render(context, request))

@permission_required(Permission.ParameterEdit)
@project_required
def edit_parameter(request: HttpRequest):
    parameter_id = request.GET.get("id")
    parameter = Parameter.objects.get(pk=parameter_id)
    project = get_project(request)
    template = loader.get_template("map/edit-parameter.html")
    context = {
        "project": project,
        "parameter": parameter,
    }
    return HttpResponse(template.render(context, request))

@permission_required(Permission.DataAdd)
@project_required
def add_data(request: HttpRequest):
    template = loader.get_template("map/add-data.html")
    context = {
    }
    return HttpResponse(template.render(context, request))

@project_required
def details(request: HttpRequest):
    template = loader.get_template(f"map/details.html")
    current_project = get_project(request)
    attributes = Measure.objects.filter(project=current_project)
    parameters = Parameter.objects.filter(project=current_project)
    context = {
        "attributes": attributes,
        "parameters": parameters,
        "project": current_project,
    }
    return HttpResponse(template.render(context, request))

def error_page(request: HttpRequest):
    template = loader.get_template(f"map/error.html")
    message = request.GET.get("msg")
    context = {
        "msg": message,
    }
    return HttpResponse(template.render(context, request))

@permission_required(Permission.AdminEditProject)
@project_required
def edit_project_details(request: HttpRequest):
    template = loader.get_template(f"map/edit-project-details.html")
    current_project = get_project(request)
    attributes = Measure.objects.filter(project=current_project)
    parameters = Parameter.objects.filter(project=current_project)
    context = {
        "attributes": attributes,
        "parameters": parameters,
        "project": current_project,
    }
    return HttpResponse(template.render(context, request))

static_whitelist = [
    "register.html",
    "create-project.html",
]

def static_html(request: HttpRequest):
    file_name = request.path.split("/")[-1]
    if file_name not in static_whitelist:
        return reponse_404(request)
    template = loader.get_template(f"map/{file_name}")
    context = {
    }
    response = HttpResponse(template.render(context, request))
    # Al ser estáticas se les puede indicar que se guarden en el caché
    response.headers["Cache-Control"] = f"max-age={60*24*14}"
    return response

def project_list(request: HttpRequest):
    try:
        next = request.GET.get("next")
    except:
        next = ""
    if next == None:
        next = ""
    print(f"next: {next}")
    template = loader.get_template(f"map/project-list.html")
    current_project = get_project(request)
    projects = Project.objects.all()
    context = {
        "projects": projects,
        "current_project": current_project,
        "next": next
    }
    return HttpResponse(template.render(context, request))

def index(request: HttpRequest):
    default_project_if_undefined(request)

    template = loader.get_template(f"map/index.html")
    project = get_project(request)

    colors = list(Color.objects.filter(project=project))
    colors.sort(key=lambda color: color.strength)

    context = {
        "project": project,
        "colors": colors
    }
    return HttpResponse(template.render(context, request))
