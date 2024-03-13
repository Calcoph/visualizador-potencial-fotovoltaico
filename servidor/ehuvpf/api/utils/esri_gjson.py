# (en bash) export PYTHONPATH=/usr/lib/python3/dist-packages
# (en powershell) $Env:PYTHONPATH="/usr/lib/python3/dist-packages"

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsMapLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem
from django.core.files.uploadedfile import UploadedFile

TEMP_PATH = "/tmp/django/file_upload/"

def save_esri(prj: UploadedFile, dbf: UploadedFile, shx: UploadedFile, shp: UploadedFile, layer_name: str):
    # TODO: potential vulnerability: unsanitized path
    # TODO: potential vulnerability: 2 uploads with the same path name might conflict
    path = f"{TEMP_PATH}{layer_name}"
    with open(path + ".prj", "wb+") as f:
        for chunk in prj.chunks():
            f.write(chunk)
    with open(path + ".dbf", "wb+") as f:
        for chunk in dbf.chunks():
            f.write(chunk)
    with open(path + ".shx", "wb+") as f:
        for chunk in shx.chunks():
            f.write(chunk)
    with open(path + ".shp", "wb+") as f:
        for chunk in shp.chunks():
            f.write(chunk)

def esri_to_geojson(qgs: QgsApplication, layer_path: str, output_path: str):
    layer: QgsVectorLayer = QgsVectorLayer(layer_path, "", "ogr")
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    QgsVectorFileWriter.writeAsVectorFormat(layer, output_path, "utf-8", crs, "GeoJSON")

def convert_esri_to_geojson(layer_path: str, output_path: str):
    layer_path = f"{TEMP_PATH}{layer_path}.shp"
    QgsApplication.setPrefixPath("/usr", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    esri_to_geojson(qgs, layer_path, output_path)
    qgs.exitQgis()

if __name__ == "__main__":
    layer_path = "EIB_eroei_filt"

    convert_esri_to_geojson(layer_path, "a.geojson")
