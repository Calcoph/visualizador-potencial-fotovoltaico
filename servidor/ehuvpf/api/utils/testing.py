def generate_placeholder_data(lat, lon):
    p1x, p1y = (lat+0.001, lon+0.001)
    p2x, p2y = (lat, lon+0.001)
    p3x, p3y = (lat, lon)
    p4x, p4y = (lat+0.001, lon)

    placeholder_data = {
        "type": "Feature",
        "properties": {"_sum": f"lat:{lat} lon:{lon}"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [p1x, p1y],
                [p2x, p2y],
                [p3x, p3y],
                [p4x, p4y]
            ]]
        }
    }

    return placeholder_data
