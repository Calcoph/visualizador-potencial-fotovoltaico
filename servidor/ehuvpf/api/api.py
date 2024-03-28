
import json
from os import makedirs
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.files.uploadedfile import UploadedFile

from .utils.esri_gjson import EsriFiles, convert_esri_to_geojson, save_esri
from .utils.testing import generate_placeholder_building

from .models import Layer, Building, Measure, Project
from .utils.session_handler import get_project, set_project
from .utils.decorators import project_required_api

RESOLUTION = 0.1
PROJECT_PATH = "/var/lib/ehuvpf/ehuvpf-projects"

def create_project(request: HttpRequest):
    name = request.POST["name"]

    project = Project(name=name)
    project.save()

    return HttpResponse("Success")


@project_required_api
def get_buildings(request: HttpRequest):
    params = request.GET
    layer_id = params.get("layer")
    lat = params.get("lat")
    lon = params.get("lon")
    # TODO: Make sure "layer" is of this project
    project = get_project(request)
    layer = Layer.objects.get(pk=layer_id)

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

    return JsonResponse(resp)

@project_required_api
def get_placeholder_buildings(request: HttpRequest):
    params = request.GET
    lat = int(params.get("lat")) * RESOLUTION
    lon = int(params.get("lon")) * RESOLUTION

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

    return JsonResponse(json_buildings)

@project_required_api
def get_attributes(request: HttpRequest):
    project = get_project(request)
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

    return JsonResponse(attributes)

class InputMethod:
    SINGLE = "single"
    MULTIPLE = "multiple"

def get_files(request: HttpRequest) -> list[EsriFiles]:
    input_method = request.POST["inputmethod"]
    files = []
    if input_method == InputMethod.SINGLE:
        prj = request.FILES["prj"]
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

@project_required_api
def add_building(request: HttpRequest):
    files = get_files(request)
    project = get_project(request)
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

    return HttpResponse("Successfully saved")

@project_required_api
def new_attribute(request: HttpRequest):
    new_name = request.POST["name"]
    display_name = request.POST["display_name"]
    project = get_project(request)

    new_measure = Measure(project=project, name=new_name, display_name=display_name)
    new_measure.save()

    return HttpResponse("Success")

@project_required_api
def edit_layer(request: HttpRequest):
    layer_id = request.POST["layer"]
    name_pattern = request.POST["name-pattern"]
    attributes = request.POST.getlist("attribute")
    color_attribute_id = request.POST["color-attribute"]

    layer = Layer.objects.get(pk=layer_id)
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

    return HttpResponse("Success")

@project_required_api
def add_layer(request: HttpRequest):
    # TODO: add validation
    # TODO Make sure that no other layer exists with this name on this project
    layer_name = request.POST["layer-name"]
    attributes = request.POST.getlist("attributes")
    color_measure = request.POST["color-attribute"]
    name_pattern = request.POST["name-pattern"]
    # TODO: Asegurarse que name_pattern no es subset de otro patrón

    project = get_project(request)

    measures = []
    for attribute in attributes:
        selected_measure = Measure.objects.get(pk=attribute)
        measures.append(selected_measure)

    color_measure = Measure.objects.get(pk=color_measure)

    new_layer = Layer(project=project, color_measure=color_measure, name=layer_name, name_pattern=name_pattern)
    new_layer.save()
    new_layer.default_measures.set(measures)

    return HttpResponse("Success")

@project_required_api
def get_layers(request: HttpRequest):
    project = get_project(request)

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
    return JsonResponse(resp)

def select_project(request: HttpRequest):
    project_id = request.POST["project_id"]
    set_project(request, project_id)

    return HttpResponse("Success")
