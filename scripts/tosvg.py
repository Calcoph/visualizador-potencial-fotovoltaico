import json
import math

import sys
def to_svg(input_file, output_file):
    with open(input_file) as f:
        features = json.load(f)["features"]

    multipolygons = []

    for feature in features:
        multipolygons.append(feature["geometry"]["coordinates"])

    def scale_coords(coords, zoom):
        for coord in coords:
            coord[0] *= zoom
            coord[1] *= zoom

    def get_min(coords) -> tuple[float, float]:
        min_x = math.inf # Infinito
        min_y = math.inf # Infinito
        for coord in coords:
            if coord[0] < min_x:
                min_x = coord[0]

            if coord[1] < min_y:
                min_y = coord[1]
        
        return min_x, min_y

    global_min_x = math.inf # Infinito
    global_min_y = math.inf # Infinito

    zoom = 3
    for multipolygon in multipolygons:
        for polygon in multipolygon:
            for coords in polygon:
                scale_coords(coords, zoom)
                min_x, min_y = get_min(coords)
                if min_x < global_min_x:
                    global_min_x = min_x
                if min_y < global_min_y:
                    global_min_y = min_y

    polygon_outputs = []
    for multipolygon in multipolygons:
        for (i, polygon) in enumerate(multipolygon):
            output = '<path d="'
            for coords in polygon:
                for (i, coord) in enumerate(coords):
                    coord[0] -= global_min_x
                    coord[1] -= global_min_y

                    letter = "L"
                    if i == 0:
                        letter = "M"

                    output += f"{letter}{coord[0]:.5g} {coord[1]:.5g} "
                output += "Z "

            if len(output) > 1:
                output = output[:-1]
            output += '" style="'
            output += 'fill:lime;'
            output += 'stroke:purple;'
            output += 'stroke-width:1;'
            output += '" />\n'
            polygon_outputs.append(output)

    header = [
        '<svg height="1000" width="1500">\n',
    ]

    footer = [
        '</svg>\n',
    ]

    with open(output_file, "w") as f:
        f.writelines(header)
        f.writelines(polygon_outputs)
        f.writelines(footer)

if __name__ == "__main__":
    print()
    if len(sys.argv) != 3:
        print("Uso incorrecto de la aplicación")
        print("Uso correcto: python tosvg.py <fichero entrada> <fichero salida>")
        print("ejemplo: python tosvg.py input.geojson www/svg/output.svg")
        sys.exit(1)
    input_file = sys.argv[1]
    print(f"Convirtiendo a svg: {input_file}")
    output_file = sys.argv[2]
    print(f"Salida: {output_file}")
    print()
    to_svg(input_file, output_file)
