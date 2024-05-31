
import json
from os import makedirs
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.decorators import permission_required

from .utils.esri_gjson import EsriFiles, convert_esri_to_geojson, save_esri
from .utils.testing import generate_placeholder_building
from .utils.user import Permission

from .models import Layer, Building, Measure, Parameter, Project, Color, ColorRule
from .utils.session_handler import get_project, set_project
from .utils.decorators import project_required_api

RESOLUTION = 0.1
PROJECT_PATH = "/var/lib/ehuvpf/ehuvpf-projects"

@permission_required(Permission.ProjectAdd)
def create_project(request: HttpRequest):
    name = request.POST.get("name")

    create_project_impl(name)

    return HttpResponse("Success")

def create_project_impl(name: str):
    project = Project(name=name)
    project.save()

# @permission_required(Permission.BuildingView) # Commented out because this should be accessible by anyone
@project_required_api
def get_buildings(request: HttpRequest):
    layer_id = request.GET.get("layer")
    lat = request.GET.get("lat")
    lat = int(lat)
    lon = request.GET.get("lon")
    lon = int(lon)
    project = get_project(request)
    layer = Layer.objects.get(pk=layer_id)

    resp = get_buildings_impl(project, layer, lat, lon, layer_id)

    return JsonResponse(resp)

def get_buildings_impl(project: Project, layer: Layer, lat: int, lon: int, layer_id: str):
    # TODO: Make sure "layer" is of this project
    buildings = Building.objects.filter(layer=layer, lat=lat, lon=lon)
    json_buildings = []
    for building in buildings:
        with open(building.path, "r") as f:
            building = json.load(f)
            json_buildings.append(building)

    resp = {
        "layer": layer_id,
        "buildings": json_buildings
    }

    return resp

@project_required_api
def get_placeholder_buildings(request: HttpRequest):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    lat = int(lat) * RESOLUTION
    lon = int(lon) * RESOLUTION

    json_buildings = get_placeholder_buildings_impl(lat, lon)

    return JsonResponse(json_buildings)

def get_placeholder_buildings_impl(lat: int, lon: int) -> dict[str]:
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

    return json_buildings

# @permission_required(Permission.MeasureView) # Commented out because this should be accessible by anyone
@project_required_api
def get_attributes(request: HttpRequest):
    project = get_project(request)

    attributes = get_attributes_impl(project)

    return JsonResponse(attributes)

def get_attributes_impl(project: Project):
    measures = Measure.objects.filter(project=project)
    measure_list = []
    for measure in measures:
        measure_list.append({
            "name": measure.name,
            "display_name": measure.display_name,
        })

    attributes = {
        "available_attributes": measure_list
    }

    return attributes

class InputMethod:
    SINGLE = "single"
    MULTIPLE = "multiple"

def get_files(request: HttpRequest) -> list[EsriFiles]:
    input_method = request.POST.get("inputmethod")
    files = []
    if input_method == InputMethod.SINGLE:
        prj = request.FILES.get("prj")
        name = prj.name.split(".prj")[0]
        files.append(
            EsriFiles(
                name,
                prj,
                request.FILES["dbf"],
                request.FILES["shx"],
                request.FILES["shp"]
            )
        )
    elif input_method == InputMethod.MULTIPLE:
        multiple = request.FILES.getlist("multiple_files")
        file_dict: dict[str, list[UploadedFile]] = {}
        # Agrupa todos los ficheros según su nombre (en teoría cada nombre debe tener 4 ficheros)
        for file in multiple:
            file_name = file.name.split(".")[0]
            if file_name in file_dict:
                file_dict[file_name].append(file)
            else:
                file_dict[file_name] = [file]
        for (file_name, file_list) in file_dict.items():
            prj = None
            dbf = None
            shx = None
            shp = None
            for file in file_list:
                # TODO: Asegurarse que "file.name" sólo tiene un "."
                extension = file.name.split(".")[1]
                if extension == "prj":
                    prj = file
                elif extension == "dbf":
                    dbf = file
                elif extension == "shx":
                    shx = file
                elif extension == "shp":
                    shp = file
            # Asegurarse de que los 4 ficheros han sido enviados
            if (prj is not None
                and dbf is not None
                and shx is not None
                and shp is not None
            ):
                files.append(EsriFiles(file_name, prj, dbf, shx, shp))
            else:
                # TODO: Notificar usuario
                pass
    else:
        # TODO
        raise Exception()

    return files

@permission_required(Permission.BuildingAdd)
@project_required_api
def add_building(request: HttpRequest):
    files = get_files(request)
    project = get_project(request)

    add_building_impl(project, files)

    return HttpResponse("Successfully saved")

def add_building_impl(project: Project, files: list[EsriFiles]):
    layers = Layer.objects.filter(project=project)
    for esri_files in files:
        selected_layer = None
        for layer in layers:
            if layer.name_pattern in esri_files.name:
                selected_layer = layer
                break

        if selected_layer is None:
            # TODO: Notify user
            raise Exception()
        path = f"{PROJECT_PATH}/{project.pk}/{selected_layer.name}"
        makedirs(path, exist_ok=True)

        save_esri(esri_files)
        new_path = path + f"/{esri_files.name}.geojson"
        (output_path, lat, lon) = convert_esri_to_geojson(esri_files.name, new_path)

        # Update database
        building = Building(layer=selected_layer, path=output_path, lat=lat, lon=lon)
        building.save()

@permission_required(Permission.MeasureAdd)
@project_required_api
def add_attribute(request: HttpRequest):
    name = request.POST.get("name")
    display_name = request.POST.get("display_name")
    description = request.POST.get("description")
    unit = request.POST.get("unit")
    project = get_project(request)

    add_attribute_impl(project, name, display_name, description, unit)

    return HttpResponse("Success")

def add_attribute_impl(project: Project, name: str, display_name: str, description: str, unit: str):
    new_measure = Measure(project=project, name=name, display_name=display_name, description=description, unit=unit)
    new_measure.save()

@permission_required(Permission.MeasureEdit)
@project_required_api
def edit_attribute(request: HttpRequest):
    name = request.POST.get("name")
    display_name = request.POST.get("display_name")
    description = request.POST.get("description")
    unit = request.POST.get("unit")
    id = request.POST.get("id")
    project = get_project(request)

    edit_attribute_impl(name, display_name, description, unit, id)

    return HttpResponse("Success")

def edit_attribute_impl(name: str, display_name: str, description: str, unit: str, id: str):
    editing_attribute = Measure.objects.get(pk=id)
    editing_attribute.name = name
    editing_attribute.display_name = display_name
    editing_attribute.description = description
    editing_attribute.unit = unit

    editing_attribute.save()

@permission_required(Permission.ParameterAdd)
@project_required_api
def add_parameter(request: HttpRequest):
    name = request.POST.get("name")
    description = request.POST.get("description")
    value = request.POST.get("value")
    project = get_project(request)

    add_parameter_impl(project, name, description, value)

    return HttpResponse("Success")

def add_parameter_impl(project: Project, name: str, description: str, value: str):
    parameter = Parameter(project=project, name=name, description=description, value=value)
    parameter.save()

@permission_required(Permission.ParameterEdit)
@project_required_api
def edit_parameter(request: HttpRequest):
    name = request.POST.get("name")
    description = request.POST.get("description")
    value = request.POST.get("value")
    id = request.POST.get("id")
    project = get_project(request)

    edit_parameter_impl(name, description, value, id)

    return HttpResponse("Success")

def edit_parameter_impl(name: str, description: str, value: str, id: str):
    print(id)
    parameter = Parameter.objects.get(pk=id)
    parameter.name = name
    parameter.description = description
    parameter.value = value

    parameter.save()

@permission_required(Permission.LayerEdit)
@project_required_api
def edit_layer(request: HttpRequest):
    layer_id = request.POST.get("layer")
    name_pattern = request.POST.get("name-pattern")
    attributes = request.POST.getlist("attribute")
    color_attribute_id = request.POST.get("color-attribute")
    new_color_rules = request.POST.getlist("color_rule")

    new_color_rules = list(map(lambda color_rule: float(color_rule.replace(",", ".")), new_color_rules))
    layer = Layer.objects.get(pk=layer_id)

    edit_layer_impl(layer, name_pattern, attributes, color_attribute_id, new_color_rules)

    return HttpResponse("Success")

def edit_layer_impl(layer: Layer, name_pattern: str, attributes: list[str], color_attribute_id: str, new_color_rules: list[float]):
    for rule in layer.color_rules.all():
        rule: ColorRule
        new_minimum = new_color_rules[rule.color.strength]
        rule.minimum = new_minimum
        rule.save()

    # TODO: Asegurarse que name_pattern no es subset de otro patrón
    layer.name_pattern = name_pattern
    color_attribute = Measure.objects.get(pk=color_attribute_id)
    # TODO: Validation
    layer.color_measure = color_attribute

    measures = []
    for attribute_id in attributes:
        # TODO: Validation
        measures.append(Measure.objects.get(pk=attribute_id))
    layer.default_measures.set(measures)

    layer.save()

@permission_required(Permission.LayerAdd)
@project_required_api
def add_layer(request: HttpRequest):
    # TODO: add validation
    # TODO Make sure that no other layer exists with this name on this project
    layer_name = request.POST.get("layer-name")
    attributes = request.POST.getlist("attributes")
    color_measure = request.POST.get("color-attribute")
    name_pattern = request.POST.get("name-pattern")
    project = get_project(request)

    add_layer_impl(project, layer_name, attributes, color_measure, name_pattern)

    return HttpResponse("Success")

def add_layer_impl(project: Project, layer_name: str, attributes: list[str], color_measure: str, name_pattern: str):
    # TODO: Asegurarse que name_pattern no es subset de otro patrón
    measures = []
    for attribute in attributes:
        selected_measure = Measure.objects.get(pk=attribute)
        measures.append(selected_measure)

    color_measure = Measure.objects.get(pk=color_measure)

    new_layer = Layer(project=project, color_measure=color_measure, name=layer_name, name_pattern=name_pattern)
    new_layer.save()
    new_layer.default_measures.set(measures)

# @permission_required(Permission.LayerView) # Commented out because this should be accessible by anyone
@project_required_api
def get_layers(request: HttpRequest):
    project = get_project(request)

    resp = get_layers_impl(project)

    return JsonResponse(resp)

def get_layers_impl(project: Project):
    layers = Layer.objects.filter(project=project)
    json_layers = []
    for layer in layers:
        measures = []
        for measure in layer.default_measures.all():
            measures.append({
                "name": measure.name,
                "display_name": measure.display_name
            })
        json_layers.append({
            "name": layer.name,
            "measures": measures,
            "color_measure": layer.color_measure.name,
            "id": layer.pk
        })

    resp = {
        "layers": json_layers
    }

    return resp


# @permission_required(Permission.ColorView) # Commented out because this should be accessible by anyone
@project_required_api
def get_colors(request: HttpRequest):
    project = get_project(request)

    resp = get_colors_impl(project)

    return JsonResponse(resp)

def get_colors_impl(project: Project):
    colors = list(Color.objects.filter(project=project))
    colors.sort(key=lambda color: color.strength)
    json_colors = []
    for color in colors:
        json_colors.append(color.hex)

    minimums = {}
    layers = Layer.objects.filter(project=project)
    for layer in layers:
        color_rules = list(layer.color_rules.all())
        color_rules.sort(key=lambda color_rule: color_rule.color.strength)
        layer_minimums = list(map(lambda color_rule: color_rule.minimum, color_rules))
        minimums[str(layer.pk)] = layer_minimums

    resp = {
        "colors": json_colors,
        "minimums": minimums
    }

    return resp

@permission_required(Permission.ColorEdit)
@project_required_api
def update_colors(request: HttpRequest):
    colors = request.POST.getlist("color")
    project = get_project(request)

    update_colors_impl(project, colors)

    return HttpResponse(colors)

def update_colors_impl(project: Project, colors: list[str]):
    colores_proyecto = list(Color.objects.filter(project=project))
    colores_proyecto.sort(key=lambda color: color.strength)
    for (strength, color) in enumerate(colors):
        if strength < len(colores_proyecto):
            # Edita un color existente
            color_existente = colores_proyecto[strength]
            color_existente.hex = color
            color_existente.save()
        else:
            # Añade un nuevo color
            new_color = Color(project=project, hex=color, strength=strength)
            new_color.save()

    # Borra los colores con strength > len(colors) (no se ha enviado estos colores)
    i = len(colors)
    while i < len(colores_proyecto):
        colores_proyecto[i].delete()
        i += 1

# @permission_required(Permission.ProjectView) # Commented out because this should be accessible by anyone
def select_project(request: HttpRequest):
    project_id = request.POST.get("project_id")
    set_project(request, project_id)

    return HttpResponse("Success")
