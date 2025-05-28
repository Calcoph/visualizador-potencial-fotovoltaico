# (en bash) export PYTHONPATH=/usr/lib/python3/dist-packages
# (en powershell) $Env:PYTHONPATH="/usr/lib/python3/dist-packages"

from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem, QgsRectangle, QgsCoordinateTransform, QgsCoordinateTransformContext
from django.core.files.uploadedfile import UploadedFile
from ..api import RESOLUTION

TEMP_PATH = "/tmp/django/file_upload/"

class EsriFiles:
    def __init__(self, name: str, prj: UploadedFile, dbf: UploadedFile, shx: UploadedFile, shp: UploadedFile) -> None:
        self.name = name
        self.prj = prj
        self.dbf = dbf
        self.shx = shx
        self.shp = shp

def save_esri(esri_files: EsriFiles):
    # TODO: potential vulnerability: unsanitized path
    # TODO: potential vulnerability: 2 uploads with the same path name might conflict
    path = f"{TEMP_PATH}{esri_files.name}"
    with open(path + ".prj", "wb+") as f:
        for chunk in esri_files.prj.chunks():
            f.write(chunk)
    with open(path + ".dbf", "wb+") as f:
        for chunk in esri_files.dbf.chunks():
            f.write(chunk)
    with open(path + ".shx", "wb+") as f:
        for chunk in esri_files.shx.chunks():
            f.write(chunk)
    with open(path + ".shp", "wb+") as f:
        for chunk in esri_files.shp.chunks():
            f.write(chunk)

def esri_to_geojson(layer_path: str, output_path: str) -> tuple[str, int, int]:
    # Read the files in TEMP_PATH
    layer: QgsVectorLayer = QgsVectorLayer(layer_path, "", "ogr")

    # Get the center of the layer
    bounding_box = QgsRectangle()
    destination_crs = QgsCoordinateReferenceSystem("EPSG:4326")# 4326 is the standard longitude/latitude, which is whate leaflet returns
    # Save to geojson
    QgsVectorFileWriter.writeAsVectorFormat(layer, output_path, "utf-8", destination_crs, "GeoJSON")

    source_crs = layer.crs()
    # Need to transform the coordinate system to lat/long since we don't know the layer's crs
    # But we know what will leaflet use
    crs_transform = QgsCoordinateTransform(source_crs, destination_crs, QgsCoordinateTransformContext())
    for feature in layer.getFeatures():
        geometry = feature.geometry()
        geometry.transform(crs_transform)
        new_bounding_box = geometry.boundingBox()
        bounding_box.combineExtentWith(new_bounding_box)

    center = bounding_box.center()
    lat = int(center.x() / RESOLUTION)
    lon = int(center.y() / RESOLUTION)

    return (output_path, lat, lon)

def convert_esri_to_geojson(layer_path: str, output_path: str) -> tuple[str, int, int]:
    # TODO: Is this function really needed?
    layer_path = f"{TEMP_PATH}{layer_path}.shp"
    return esri_to_geojson(layer_path, output_path)

if __name__ == "__main__":
    layer_path = "EIB_eroei_filt"

    convert_esri_to_geojson(layer_path, "a.geojson")
