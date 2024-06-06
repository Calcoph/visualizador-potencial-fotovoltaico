from __future__ import annotations

from http import HTTPStatus
import json
from os import makedirs
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
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

class ErrorKind:
    FORBIDDEN = 0
    BAD_REQUEST = 1

    def __init__(self, id: int) -> None:
        self.id = id

    def forbidden() -> ErrorKind:
        return ErrorKind(ErrorKind.FORBIDDEN)

    def bad_request() -> ErrorKind:
        return ErrorKind(ErrorKind.BAD_REQUEST)

class ApiError:
    def __init__(self, endpoint: str, reason: str, error_kind: ErrorKind) -> None:
        self.endpoint = endpoint
        self.reason = reason
        self.error_kind = error_kind

    def to_response(self) -> JsonResponse:
        json_resp = {
            "endpoint": self.endpoint,
            "reason": self.reason
        }
        response = JsonResponse(json_resp)
        if self.error_kind.id == ErrorKind.FORBIDDEN:
            response.status_code = HTTPStatus.FORBIDDEN
        if self.error_kind.id == ErrorKind.BAD_REQUEST:
            response.status_code = HTTPStatus.BAD_REQUEST

        return response

class GetBuildingsParams:
    def __init__(self, layer: Layer, lat: int, lon: int) -> None:
        self.layer = layer
        self.lat = lat
        self.lon = lon

    def validate(request: HttpRequest, project: Project) -> GetBuildingsParams | ApiError:
        endpoint = "get_buildings"

        # Method check
        method = "GET"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        layer_param_name = "layer"
        try:
            layer_id = request.GET.get(layer_param_name)
        except:
            return ApiError(endpoint, f'"{layer_param_name}" is required', ErrorKind.BAD_REQUEST)
        lat_param_name = "lat"
        try:
            lat = request.GET.get(lat_param_name)
        except:
            return ApiError(endpoint, f'"{lat_param_name}" is required', ErrorKind.BAD_REQUEST)
        lon_param_name = "lon"
        try:
            lon = request.GET.get(lon_param_name)
        except:
            return ApiError(endpoint, f'"{lon_param_name}" is required', ErrorKind.BAD_REQUEST)

        # Parameter types
        try:
            lat = int(lat)
        except:
            return ApiError(endpoint, f'"{lat_param_name}" must be an integer', ErrorKind.BAD_REQUEST)
        try:
            lon = int(lon)
        except:
            return ApiError(endpoint, f'"{lon_param_name}" must be an integer', ErrorKind.BAD_REQUEST)
        try:
            layer = Layer.objects.get(pk=layer_id)
        except:
            return ApiError(endpoint, f'"{layer_param_name}" must be the id of an existing layer', ErrorKind.BAD_REQUEST)

        # Integrity check
        if layer.project.pk != project.pk:
            return ApiError(endpoint, f'"{layer_param_name}" must be the id of a layer of the selected project', ErrorKind.BAD_REQUEST)

        return GetBuildingsParams(layer, lat, lon)

# @permission_required(Permission.BuildingView) # Commented out because this should be accessible by anyone
@project_required_api
def get_buildings(request: HttpRequest):
    project = get_project(request)

    parameters = GetBuildingsParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        response = get_buildings_impl(parameters)
        return JsonResponse(response)

def get_buildings_impl(parameters: GetBuildingsParams):
    buildings = Building.objects.filter(layer=parameters.layer, lat=parameters.lat, lon=parameters.lon)
    json_buildings = []
    for building in buildings:
        with open(building.path, "r") as f:
            building = json.load(f)
            json_buildings.append(building)

    resp = {
        "layer": parameters.layer.pk,
        "buildings": json_buildings
    }

    return resp

class GetPlaceholderBuildingsParams:
    def __init__(self, lat: int, lon: int) -> None:
        self.lat = lat
        self.lon = lon

    def validate(request: HttpRequest) -> GetPlaceholderBuildingsParams | ApiError:
        endpoint = "get_placeholder_buildings"

        # Method check
        method = "GET"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        lat_param_name = "lat"
        try:
            lat = request.GET.get(lat_param_name)
        except:
            return ApiError(endpoint, f'"{lat_param_name}" is required', ErrorKind.BAD_REQUEST)
        lon_param_name = "lon"
        try:
            lon = request.GET.get(lon_param_name)
        except:
            return ApiError(endpoint, f'"{lon_param_name}" is required', ErrorKind.BAD_REQUEST)

        # Parameter types
        try:
            lat = int(lat)
        except:
            return ApiError(endpoint, f'"{lat_param_name}" must be an integer', ErrorKind.BAD_REQUEST)
        try:
            lon = int(lon)
        except:
            return ApiError(endpoint, f'"{lon_param_name}" must be an integer', ErrorKind.BAD_REQUEST)

        return GetPlaceholderBuildingsParams(lat, lon)

def get_placeholder_buildings(request: HttpRequest):
    parameters = GetPlaceholderBuildingsParams.validate(request)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        response = get_placeholder_buildings_impl(parameters)
        return JsonResponse(response)

def get_placeholder_buildings_impl(parameters: GetPlaceholderBuildingsParams) -> dict[str]:
    # Resolution adjustment
    lat = parameters.lat * RESOLUTION
    lon = parameters.lon * RESOLUTION
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

def get_files(parameters: AddBuildingParams) -> list[EsriFiles]:
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

class AddBuildingParams:
    def __init__(self, files: dict[str, dict[str, UploadedFile]]) -> None:
        self.files = files

    def validate(request: HttpRequest) -> AddBuildingParams | ApiError:
        endpoint = "add_building"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        input_method_param_name = "inputmethod"
        try:
            input_method = request.POST.get(input_method_param_name)
        except:
            return ApiError(endpoint, f'"{input_method_param_name}" is required', ErrorKind.BAD_REQUEST)

        files: dict[str, dict[str, UploadedFile]] = []
        if input_method == InputMethod.SINGLE:
            prj_file_name = "prj"
            try:
                prj = request.FILES.get(prj_file_name)
            except:
                return ApiError(endpoint, f'"{prj_file_name}" file is required when using "single" input method', ErrorKind.BAD_REQUEST)
            dbf_file_name = "dbf"
            try:
                dbf = request.FILES.get(dbf_file_name)
            except:
                return ApiError(endpoint, f'"{dbf_file_name}" file is required when using "single" input method', ErrorKind.BAD_REQUEST)
            shx_file_name = "shx"
            try:
                shx = request.FILES.get(shx_file_name)
            except:
                return ApiError(endpoint, f'"{shx_file_name}" file is required when using "single" input method', ErrorKind.BAD_REQUEST)
            shp_file_name = "shp"
            try:
                shp = request.FILES.get(shp_file_name)
            except:
                return ApiError(endpoint, f'"{shp_file_name}" file is required when using "single" input method', ErrorKind.BAD_REQUEST)

            # File extension check
            if not prj.name.endswith(".prj"):
                return ApiError(endpoint, f'"{prj_file_name}" file must end in ".prj"', ErrorKind.BAD_REQUEST)
            if not dbf.name.endswith(".dbf"):
                return ApiError(endpoint, f'"{dbf_file_name}" file must end in ".dbf"', ErrorKind.BAD_REQUEST)
            if not shx.name.endswith(".shx"):
                return ApiError(endpoint, f'"{shx_file_name}" file must end in ".shx"', ErrorKind.BAD_REQUEST)
            if not shp.name.endswith(".shp"):
                return ApiError(endpoint, f'"{shp_file_name}" file must end in ".shp"', ErrorKind.BAD_REQUEST)

            file_name = file.name.split(".")[-1]
            files[file_name] = {
                "prj": prj,
                "dbf": dbf,
                "shx": shx,
                "shp": shp
            }
        elif input_method == InputMethod.MULTIPLE:
            multiple = request.FILES.getlist("multiple_files")
            if len(multiple) == 0:
                return ApiError(endpoint, f'{input_method_param_name} was "{InputMethod.MULTIPLE}" but no files were sent', ErrorKind.BAD_REQUEST)

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
                    return ApiError(endpoint, f'Layer "{file_name}" doesn\'t have any file ending in ".prj"', ErrorKind.BAD_REQUEST)
                if "dbf" not in file_dict:
                    return ApiError(endpoint, f'Layer "{file_name}" doesn\'t have any file ending in ".dbf"', ErrorKind.BAD_REQUEST)
                if "shx" not in file_dict:
                    return ApiError(endpoint, f'Layer "{file_name}" doesn\'t have any file ending in ".shx"', ErrorKind.BAD_REQUEST)
                if "shp" not in file_dict:
                    return ApiError(endpoint, f'Layer "{file_name}" doesn\'t have any file ending in ".shp"', ErrorKind.BAD_REQUEST)

                if len(file_dict) != 4:
                    return ApiError(endpoint, f'Layer "{file_name}" contains a file that doesn\'t end in ".prj", ".dbf", ".shx", ".shp"', ErrorKind.BAD_REQUEST)
        else:
            return ApiError(endpoint, f'{input_method_param_name} must be one of ["{InputMethod.SINGLE}", "{InputMethod.MULTIPLE}"] but was {input_method}', ErrorKind.BAD_REQUEST)

        return AddBuildingParams(files)

@permission_required(Permission.BuildingAdd)
@project_required_api
def add_building(request: HttpRequest):
    project = get_project(request)

    parameters = AddBuildingParams.validate(request)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        files = get_files(parameters)
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

class AddAttributeParams:
    def __init__(self, name: str, display_name: str, description: str, unit: str) -> None:
        self.name = name
        self.display_name = display_name
        self.description = description
        self.unit = unit

    def validate(request: HttpRequest) -> AddAttributeParams | ApiError:
        endpoint = "add_attribute"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "name"
        try:
            name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "display_name"
        try:
            display_name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "description"
        try:
            description = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "unit"
        try:
            unit = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        return AddAttributeParams(name, display_name, description, unit)

@permission_required(Permission.MeasureAdd)
@project_required_api
def add_attribute(request: HttpRequest):
    project = get_project(request)

    parameters = AddAttributeParams.validate(request)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        add_attribute_impl(project, parameters)
        return HttpResponse("Success")

def add_attribute_impl(project: Project, parameters: AddAttributeParams):
    new_measure = Measure(
        project=project,
        name=parameters.name,
        display_name=parameters.display_name,
        description=parameters.description,
        unit=parameters.unit
    )
    new_measure.save()

class EditAttributeParams:
    def __init__(self, name: str, display_name: str, description: str, unit: str, attribute: Measure) -> None:
        self.name = name
        self.display_name = display_name
        self.description = description
        self.unit = unit
        self.attribute = attribute

    def validate(request: HttpRequest, project: Project) -> EditAttributeParams | ApiError:
        endpoint = "edit_attribute"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "name"
        try:
            name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "display_name"
        try:
            display_name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "description"
        try:
            description = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "unit"
        try:
            unit = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        attribute_id_param_name = "id"
        try:
            id = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        try:
            attribute = Measure.objects.get(pk=id)
        except:
            return ApiError(endpoint, f'"{attribute_id_param_name}" must be the id of an existing attribute', ErrorKind.BAD_REQUEST)

        # Integrity check
        if attribute.project.pk != project.pk:
            return ApiError(endpoint, f'"{attribute_id_param_name}" must be the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)

        return EditAttributeParams(name, display_name, description, unit, attribute)

@permission_required(Permission.MeasureEdit)
@project_required_api
def edit_attribute(request: HttpRequest):
    project = get_project(request)

    parameters = EditAttributeParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_attribute_impl(parameters)
        return HttpResponse("Success")

def edit_attribute_impl(parameters: EditAttributeParams):
    editing_attribute = parameters.attribute
    editing_attribute.name = parameters.name
    editing_attribute.display_name = parameters.display_name
    editing_attribute.description = parameters.description
    editing_attribute.unit = parameters.unit

    editing_attribute.save()

class AddParameterParams:
    def __init__(self, name: str, description: str, value: str) -> None:
        self.name = name
        self.description = description
        self.value = value

    def validate(request: HttpRequest) -> AddParameterParams | ApiError:
        endpoint = "add_parameter"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "name"
        try:
            name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        param_name = "description"
        try:
            description = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "value"
        try:
            value = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        return AddParameterParams(name, description, value)

@permission_required(Permission.ParameterAdd)
@project_required_api
def add_parameter(request: HttpRequest):
    project = get_project(request)

    parameters = AddParameterParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        add_parameter_impl(parameters, project)
        return HttpResponse("Success")

def add_parameter_impl(parameters: AddParameterParams, project: Project):
    parameter = Parameter(
        project=project,
        name=parameters.name,
        description=parameters.description,
        value=parameters.value
    )
    parameter.save()

class EditParameterParams:# TODO: Delete this class
    def __init__(self, name: str, description: str, value: str, parameter: Parameter) -> None:
        self.name = name
        self.description = description
        self.value = value
        self.parameter = parameter

    def validate(request: HttpRequest, project: Project) -> EditParameterParams | ApiError:
        endpoint = "edit_parameter"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "name"
        try:
            name = request.GET.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "description"
        try:
            description = request.GET.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "value"
        try:
            value = request.GET.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        parameter_id_param_name = "id"
        try:
            id = request.GET.get(parameter_id_param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        try:
            parameter = Parameter.objects.get(pk=id)
        except:
            return ApiError(endpoint, f'"{parameter_id_param_name}" must be the id of an existing parameter', ErrorKind.BAD_REQUEST)

        # Integrity check
        if parameter.project.pk != project.pk:
            return ApiError(endpoint, f'"{parameter_id_param_name}" must be the id of a parameter of the selected project', ErrorKind.BAD_REQUEST)

        return EditParameterParams(name, description, value, parameter)

@permission_required(Permission.ParameterEdit)
@project_required_api
def edit_parameter(request: HttpRequest):
    project = get_project(request)

    parameters = AddParameterParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_parameter_impl(parameters)
        return HttpResponse("Success")


def edit_parameter_impl(parameters: EditParameterParams):
    parameter = parameters.parameter
    parameter.name = parameters.name
    parameter.description = parameters.description
    parameter.value = parameters.value

    parameter.save()

class EditPreprocessInfoParams:# TODO: Delete this class
    def __init__(self, link: str, name: str, version: str) -> None:
        self.link = link
        self.name = name
        self.version = version

    def validate(request: HttpRequest) -> EditPreprocessInfoParams | ApiError:
        endpoint = "edit_preprocess_info"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "preprocess_link"
        try:
            preprocess_link = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "preprocess_name"
        try:
            preprocess_name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "preprocess_version"
        try:
            preprocess_version = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        return EditPreprocessInfoParams(preprocess_link, preprocess_name, preprocess_version)

@permission_required(Permission.PreprocessingInfoEdit)
@project_required_api
def edit_preprocess_info(request: HttpRequest):
    project = get_project(request)

    parameters = AddParameterParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_preprocess_info_impl(project, parameters)
        return HttpResponse("Success")

def edit_preprocess_info_impl(project: Project, parameters: EditPreprocessInfoParams):
    project.preprocess_program_link = parameters.link
    project.preprocess_program_name = parameters.name
    project.preprocess_program_version = parameters.version
    project.save()

class EditDataSourceParams:# TODO: Delete this class
    def __init__(self, data_source: str) -> None:
        self.data_source = data_source

    def validate(request: HttpRequest, project: Project) -> EditDataSourceParams | ApiError:
        endpoint = "edit_data_source"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "data_source"
        try:
            data_source = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        return EditDataSourceParams(data_source)

@permission_required(Permission.DataSourceEdit)
@project_required_api
def edit_data_source(request: HttpRequest):
    project = get_project(request)

    parameters = AddParameterParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_data_source_impl(project, parameters)
        return HttpResponse("Success")

def edit_data_source_impl(project: Project, parameters: EditDataSourceParams):
    project.data_source = parameters.data_source
    project.save()

class EditLayerParams:
    def __init__(self, layer: Layer, name_pattern: str, attribute_list: list[Measure], color_attribute: list[Measure], new_color_rules: list[float]) -> None:
        self.layer = layer
        self.name_pattern = name_pattern
        self.attribute_list = attribute_list
        self.color_attribute = color_attribute
        self.new_color_rules = new_color_rules

    def validate(request: HttpRequest, project: Project) -> EditLayerParams | ApiError:
        endpoint = "edit_layer"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        layer_param_name = "layer"
        try:
            layer = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "name-pattern"
        try:
            name_pattern = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        attribute_param_name = "attribute"
        try:
            attributes = request.POST.getlist(attribute_param_name)
        except:
            return ApiError(endpoint, f'"{attribute_param_name}" is required', ErrorKind.BAD_REQUEST)
        color_attribute_param_name = "color-attribute"
        try:
            color_attribute = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        color_rule_param_name = "color_rule"
        try:
            color_rules = request.POST.getlist(color_rule_param_name)
        except:
            return ApiError(endpoint, f'"{color_rule_param_name}" is required', ErrorKind.BAD_REQUEST)

        new_color_rules = []
        for color_rule in color_rules:
            try:
                new_color_rule = float(color_rule.replace(",", "."))
            except:
                return ApiError(endpoint, f'"{color_rule_param_name}" must be a list of floats, got: {color_rule}', ErrorKind.BAD_REQUEST)
            new_color_rules.append(new_color_rule)

        try:
            layer = Layer.objects.get(pk=layer)
        except:
            return ApiError(endpoint, f'"{layer_param_name}" must be the id of an existing layer', ErrorKind.BAD_REQUEST)
        if layer.project.pk != project.pk:
            return ApiError(endpoint, f'"{layer_param_name}" must be the id of a layer of the selected project', ErrorKind.BAD_REQUEST)

        try:
            color_attribute = Measure.objects.get(pk=color_attribute)
        except:
            return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an existing attribute', ErrorKind.BAD_REQUEST)
        if color_attribute.project.pk != project.pk:
            return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)

        attribute_list = []
        for attribute_id in attributes:
            try:
                attribute = Measure.objects.get(pk=attribute_id)
            except:
                return ApiError(endpoint, f'"{attribute_id}" is not the id of an existing attribute', ErrorKind.BAD_REQUEST)
            if attribute.project.pk != project.pk:
                return ApiError(endpoint, f'"{attribute_id}" is not the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)
            attribute_list.append(attribute)

        return EditLayerParams(layer, name_pattern, attribute_list, color_attribute, new_color_rules)

@permission_required(Permission.LayerEdit)
@project_required_api
def edit_layer(request: HttpRequest):
    project = get_project(request)

    parameters = EditLayerParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_layer_impl(parameters)
        return HttpResponse("Success")


def edit_layer_impl(params: EditLayerParams):
    layer = params.layer
    for rule in layer.color_rules.all():
        rule: ColorRule
        new_minimum = params.new_color_rules[rule.color.strength]
        rule.minimum = new_minimum
        rule.save()

    # TODO: Asegurarse que name_pattern no es subset de otro patrón
    layer.name_pattern = params.name_pattern
    layer.color_measure = params.color_attribute

    layer.default_measures.set(params.attribute_list)

    layer.save()


class TemplateParams:# TODO: Delete this class
    def __init__(self) -> None:
        pass

    def validate(request: HttpRequest, project: Project) -> TemplateParams | ApiError:
        endpoint = "TODO"

        # Method check
        method = "TODO"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "TODO"
        try:
            TODO = request.GET.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        # Parameter types
        try:
            TODO = int(TODO)
        except:
            return ApiError(endpoint, f'"{param_name}" must be an integer', ErrorKind.BAD_REQUEST)

        try:
            layer = Layer.objects.get(pk=layer_id)
        except:
            return ApiError(endpoint, f'"{layer_param_name}" must be the id of an existing layer', ErrorKind.BAD_REQUEST)

        # Integrity check
        if layer.project.pk != project.pk:
            return ApiError(endpoint, '"layer_id" must be the id of a layer of the selected project', ErrorKind.BAD_REQUEST)

        return TemplateParams(TODO)


class AddLayerParams:# TODO: Delete this class
    def __init__(self, layer_name: str, attribute_list: list[Measure], color_attribute: Measure, name_pattern: str) -> None:
        self.layer_name = layer_name
        self.attribute_list = attribute_list
        self.color_attribute = color_attribute
        self.name_pattern = name_pattern

    def validate(request: HttpRequest, project: Project) -> AddLayerParams | ApiError:
        # TODO Make sure that no other layer exists with this name on this project
        endpoint = "add_layer"

        # Method check
        method = "POST"
        if request.method != method:
            return ApiError(endpoint, f'method must be "{method}"', ErrorKind.BAD_REQUEST)

        # Required parameters
        param_name = "layer-name"
        try:
            layer_name = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "attributes"
        try:
            attributes = request.POST.getlist(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)
        color_attribute_param_name = "color-attribute"
        try:
            color_attribute = request.POST.get(color_attribute_param_name)
        except:
            return ApiError(endpoint, f'"{color_attribute_param_name}" is required', ErrorKind.BAD_REQUEST)
        param_name = "name-pattern"
        try:
            name_pattern = request.POST.get(param_name)
        except:
            return ApiError(endpoint, f'"{param_name}" is required', ErrorKind.BAD_REQUEST)

        try:
            color_attribute = Measure.objects.get(pk=color_attribute)
        except:
            return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an existing attribute', ErrorKind.BAD_REQUEST)
        if color_attribute.project.pk != project.pk:
            return ApiError(endpoint, f'"{color_attribute_param_name}" must be the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)

        attribute_list = []
        for attribute_id in attributes:
            try:
                attribute = Measure.objects.get(pk=attribute_id)
            except:
                return ApiError(endpoint, f'"{attribute_id}" is not the id of an existing attribute', ErrorKind.BAD_REQUEST)
            if attribute.project.pk != project.pk:
                return ApiError(endpoint, f'"{attribute_id}" is not the id of an attribute of the selected project', ErrorKind.BAD_REQUEST)
            attribute_list.append(attribute)

        return AddLayerParams(layer_name, attribute_list, color_attribute, name_pattern)

@permission_required(Permission.LayerAdd)
@project_required_api
def add_layer(request: HttpRequest):
    project = get_project(request)

    parameters = AddLayerParams.validate(request, project)
    if isinstance(parameters, ApiError):
        return parameters.to_response()
    else:
        edit_layer_impl(project, parameters)
        return HttpResponse("Success")

def add_layer_impl(project: Project, params: AddLayerParams):
    # TODO: Asegurarse que name_pattern no es subset de otro patrón
    new_layer = Layer(project=project, color_measure=params.color_attribute, name=params.layer_name, name_pattern=params.name_pattern)
    new_layer.save()
    new_layer.default_measures.set(params.attribute_list)

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
        # TODO: validate color
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
