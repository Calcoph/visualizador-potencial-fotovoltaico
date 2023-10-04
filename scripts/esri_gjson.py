# (en bash) export PYTHONPATH=/usr/lib/python3/dist-packages
# (en powershell) $Env:PYTHONPATH="/usr/lib/python3/dist-packages"

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsMapLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem


def main(qgs: QgsApplication, layer_path: str):
    layer: QgsVectorLayer = QgsVectorLayer(layer_path, "name", "ogr")
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    QgsVectorFileWriter.writeAsVectorFormat(layer, "a.geojson", "utf-8", crs, "GeoJSON")

if __name__ == "__main__":

    QgsApplication.setPrefixPath("/usr", True)

    qgs = QgsApplication([], False)

    qgs.initQgis()

    main(qgs, "file_path")

    qgs.exitQgis()

