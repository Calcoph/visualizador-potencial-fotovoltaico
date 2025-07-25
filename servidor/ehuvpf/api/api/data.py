from __future__ import annotations

import json
from os import makedirs
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.decorators import permission_required
from django.utils.translation import gettext as _

from . import PROJECT_PATH, RESOLUTION

from ..utils.errors import ApiError, ErrorKind

from ..utils.esri_gjson import EsriFiles, convert_esri_to_geojson, save_esri
from ..utils.testing import generate_placeholder_data
from ..utils.user import Permission

from ..models import Layer, Data, Project
from ..utils.session_handler import get_project
from ..utils.decorators import project_required_api

class GetDataParams:
    def __init__(self, layer: Layer, lat: int, lon: int) -> None:
        self.layer = layer
        self.lat = lat
        self.lon = lon

    def validate(request: HttpRequest, project: Project) -> GetDataParams | ApiError:
        endpoint = "get_data"

        # Method check
        method = "GET"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        try:
            # Required parameters
            layer_param_name = "layer"
            layer_id = request.GET.get(layer_param_name)
            if layer_id == None:
                return ApiError(endpoint, f'"{layer_param_name}" is required', ErrorKind.bad_request())

            lat_param_name = "lat"
            lat = request.GET.get(lat_param_name)
            if lat == None:
                return ApiError(endpoint, f'"{lat_param_name}" is required', ErrorKind.bad_request())

            lon_param_name = "lon"
            lon = request.GET.get(lon_param_name)
            if lon == None:
                return ApiError(endpoint, f'"{lon_param_name}" is required', ErrorKind.bad_request())

            # Parameter types
            try:
                lat = int(lat)
            except:
                return ApiError(endpoint, f'"{lat_param_name}" must be an integer', ErrorKind.bad_request())
            try:
                lon = int(lon)
            except:
                return ApiError(endpoint, f'"{lon_param_name}" must be an integer', ErrorKind.bad_request())

            layer = Layer.objects.get(pk=layer_id)
            if layer == None:
                return ApiError(endpoint, f'"{layer_param_name}" must be the id of an existing layer', ErrorKind.bad_request())
        except:
            return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())

        # Integrity check
        if layer.project.pk != project.pk:
            return ApiError(endpoint, f'"{layer_param_name}" must be the id of a layer of the selected project', ErrorKind.bad_request())

        return GetDataParams(layer, lat, lon)

@project_required_api
def get_data(request: HttpRequest):
    project = get_project(request)

    parameters = GetDataParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        response = get_data_impl(parameters)
        return JsonResponse(response)

def get_data_impl(parameters: GetDataParams):
    data = Data.objects.filter(layer=parameters.layer, lat=parameters.lat, lon=parameters.lon)
    json_data = []
    for datum in data:
        with open(datum.path, "r") as f:
            datum = json.load(f)
            json_data.append(datum)

    resp = {
        "layer": parameters.layer.pk,
        "data": json_data
    }

    return resp

class GetPlaceholderDataParams:
    def __init__(self, lat: int, lon: int) -> None:
        self.lat = lat
        self.lon = lon

    def validate(request: HttpRequest) -> GetPlaceholderDataParams | ApiError:
        endpoint = "get_placeholder_data"

        # Method check
        method = "GET"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        try:
            # Required parameters
            lat_param_name = "lat"
            lat = request.GET.get(lat_param_name)
            if lat == None:
                return ApiError(endpoint, f'"{lat_param_name}" is required', ErrorKind.bad_request())

            lon_param_name = "lon"
            lon = request.GET.get(lon_param_name)
            if lon == None:
                return ApiError(endpoint, f'"{lon_param_name}" is required', ErrorKind.bad_request())

            # Parameter types
            try:
                lat = int(lat)
            except:
                return ApiError(endpoint, f'"{lat_param_name}" must be an integer', ErrorKind.bad_request())
            try:
                lon = int(lon)
            except:
                return ApiError(endpoint, f'"{lon_param_name}" must be an integer', ErrorKind.bad_request())
        except:
            return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())

        return GetPlaceholderDataParams(lat, lon)

def get_placeholder_data(request: HttpRequest):
    parameters = GetPlaceholderDataParams.validate(request)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        response = get_placeholder_data_impl(parameters)
        return JsonResponse(response)

def get_placeholder_data_impl(parameters: GetPlaceholderDataParams) -> dict[str]:
    # Resolution adjustment
    lat = parameters.lat * RESOLUTION
    lon = parameters.lon * RESOLUTION
    data = []
    STEPS = 10
    for x in range(0, STEPS):
        for y in range(0, STEPS):
            t_lat = lat + (x / STEPS) * RESOLUTION
            t_lon = lon + (y / STEPS) * RESOLUTION
            data.append(generate_placeholder_data(t_lat, t_lon))

    json_data = {
        "data": data
    }

    return json_data

class InputMethod:
    SINGLE = "single"
    MULTIPLE = "multiple"

def get_files(parameters: AddDataParams) -> list[EsriFiles]:
    files = []
    for (file_name, layer_files) in parameters.files.items():
        files.append(
            EsriFiles(
                file_name,
                layer_files["prj"],
                layer_files["dbf"],
                layer_files["shx"],
                layer_files["shp"]
            )
        )

    return files

class AddDataParams:
    def __init__(self, files: dict[str, dict[str, UploadedFile]]) -> None:
        self.files = files

    def validate(request: HttpRequest) -> AddDataParams | ApiError:
        endpoint = "add_data"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.bad_request())

        try:
            # Required parameters
            input_method_param_name = "inputmethod"
            input_method = request.POST.get(input_method_param_name)
            if input_method == None:
                return ApiError(endpoint, f'"{input_method_param_name}" is required', ErrorKind.bad_request())

            files: dict[str, dict[str, UploadedFile]] = {}
            if input_method == InputMethod.SINGLE:
                prj_file_name = "prj"
                prj = request.FILES.get(prj_file_name)
                if prj == None:
                    return ApiError(endpoint, f'"{prj_file_name}" file is required when using "single" input method', ErrorKind.bad_request())

                dbf_file_name = "dbf"
                dbf = request.FILES.get(dbf_file_name)
                if dbf == None:
                    return ApiError(endpoint, f'"{dbf_file_name}" file is required when using "single" input method', ErrorKind.bad_request())

                shx_file_name = "shx"
                shx = request.FILES.get(shx_file_name)
                if shx == None:
                    return ApiError(endpoint, f'"{shx_file_name}" file is required when using "single" input method', ErrorKind.bad_request())

                shp_file_name = "shp"
                shp = request.FILES.get(shp_file_name)
                if shp == None:
                    return ApiError(endpoint, f'"{shp_file_name}" file is required when using "single" input method', ErrorKind.bad_request())

                # File extension check
                if not prj.name.endswith(".prj"):
                    return ApiError(endpoint, f'"{prj_file_name}" file must end in ".prj"', ErrorKind.bad_request())
                if not dbf.name.endswith(".dbf"):
                    return ApiError(endpoint, f'"{dbf_file_name}" file must end in ".dbf"', ErrorKind.bad_request())
                if not shx.name.endswith(".shx"):
                    return ApiError(endpoint, f'"{shx_file_name}" file must end in ".shx"', ErrorKind.bad_request())
                if not shp.name.endswith(".shp"):
                    return ApiError(endpoint, f'"{shp_file_name}" file must end in ".shp"', ErrorKind.bad_request())

                file_name = prj.name.split(".")[-2]
                files[file_name] = {
                    "prj": prj,
                    "dbf": dbf,
                    "shx": shx,
                    "shp": shp
                }
            elif input_method == InputMethod.MULTIPLE:
                multiple = request.FILES.getlist("multiple_files")
                if len(multiple) == 0:
                    return ApiError(endpoint, f'{input_method_param_name} was "{InputMethod.MULTIPLE}" but no files were sent', ErrorKind.bad_request())

                # Group all files by their names
                for file in multiple:
                    file_name_parts = file.name.split(".")
                    file_extension = file_name_parts[-1]
                    file_name = file_name_parts[:-1] # Everything except the extension
                    file_name = ".".join(file_name)
                    if file_name in files:
                        files[file_name][file_extension] = file
                    else:
                        files[file_name] = {
                            file_extension: file
                        }
                # Validate the groups
                for (file_name, file_dict) in files.items():
                    if "prj" not in file_dict:
                        return ApiError(endpoint, f'Layer "{file_name}" doesn\'t have any file ending in ".prj"', ErrorKind.bad_request())
                    if "dbf" not in file_dict:
                        return ApiError(endpoint, f'Layer "{file_name}" doesn\'t have any file ending in ".dbf"', ErrorKind.bad_request())
                    if "shx" not in file_dict:
                        return ApiError(endpoint, f'Layer "{file_name}" doesn\'t have any file ending in ".shx"', ErrorKind.bad_request())
                    if "shp" not in file_dict:
                        return ApiError(endpoint, f'Layer "{file_name}" doesn\'t have any file ending in ".shp"', ErrorKind.bad_request())

                    if len(file_dict) != 4:
                        return ApiError(endpoint, f'Layer "{file_name}" contains a file that doesn\'t end in ".prj", ".dbf", ".shx", ".shp"', ErrorKind.bad_request())
            else:
                return ApiError(endpoint, f'{input_method_param_name} must be one of ["{InputMethod.SINGLE}", "{InputMethod.MULTIPLE}"] but was {input_method}', ErrorKind.bad_request())
        except:
            return ApiError(endpoint, "Unknown internal server error", ErrorKind.internal_server_error())

        return AddDataParams(files)

@permission_required(Permission.DataAdd)
@project_required_api
def add_data(request: HttpRequest):
    project = get_project(request)

    parameters = AddDataParams.validate(request)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        files = get_files(parameters)
        response = add_data_impl(project, files)
        return response

def add_data_impl(project: Project, files: list[EsriFiles]):
    endpoint = "add_data"

    layers = Layer.objects.filter(project=project)
    patterns = []
    for layer in layers:
        patterns.append(layer.name_pattern)

    selected_layers = []
    for esri_files in files:
        selected_layer = None
        for layer in layers:
            if layer.name_pattern in esri_files.name:
                selected_layer = layer
                break

        if selected_layer is None:
            return ApiError(endpoint, f"No layer matches the names of the submitted files: {esri_files.name}", ErrorKind.bad_request()).to_response() # TODO: Translate
            # old text: raise Exception(f"{patterns}\n{esri_files.name}")
        path = f"{PROJECT_PATH}/{project.pk}/{selected_layer.name}" # TODO: input sanitization
        makedirs(path, exist_ok=True)

        save_esri(esri_files)
        new_path = path + f"/{esri_files.name}.geojson"
        (output_path, lat, lon) = convert_esri_to_geojson(esri_files.name, new_path)

        # Update database
        data = Data(layer=selected_layer, path=output_path, lat=lat, lon=lon)
        data.save()

        selected_layers.append(f"{esri_files.name}: {selected_layer.name}")

    response = ",".join(selected_layers)
    return HttpResponse(response)
