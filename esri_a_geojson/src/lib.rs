use json::{object::Object, JsonValue, array, number::Number};
use lector_esri::{Error, Record, Shape, ShapeType, Point};

pub fn convert_esri_to_geojson(shape_file: &[u8], index_file: &[u8], dbase_file: &[u8], name: &str) -> Result<JsonValue, Error> {
    let records = lector_esri::read_bytes(shape_file, index_file, dbase_file)?;
    dbg!(records[0].as_ref().unwrap().shape_type);
    dbg!(records[1].as_ref().unwrap().shape_type);
    let records = records.into_iter()
        .filter_map(|record| record)
        .collect();
    let records = convert_records(records);
    let mut geojson = Object::new();
    geojson.insert("type", "FeatureCollection".into());
    geojson.insert("name", name.into());
    geojson.insert("features", records.into());

    let geojson = JsonValue::Object(geojson);

    Ok(geojson)
}

fn convert_records(records: Vec<Record>) -> Vec<Object> {
    let mut values = Vec::new();
    for record in records.into_iter() {
        if let Some(geometry) = convert_record(record) {
            let mut new_value = Object::new();
            new_value.insert("type", "Feature".into());
            new_value.insert("properties", JsonValue::Object(Object::new()));
            new_value.insert("geometry", geometry.into());

            values.push(new_value)
        }
    }

    values
}

fn convert_record(record: Record) -> Option<Object> {
    let geometry_type = match record.shape_type {
        ShapeType::Null => return None,
        ShapeType::Point => GeometryType::Point,
        ShapeType::PolyLine => return None,
        ShapeType::Polygon => GeometryType::Polygon,
        ShapeType::MultiPoint => GeometryType::MultiPoint,
        ShapeType::PointZ => GeometryType::Point,
        ShapeType::PolyLineZ => return None,
        ShapeType::PolygonZ => GeometryType::Polygon,
        ShapeType::MultiPointZ => GeometryType::MultiPoint,
        ShapeType::PointM => GeometryType::Point,
        ShapeType::PolyLineM => return None,
        ShapeType::PolygonM => GeometryType::Polygon,
        ShapeType::MultiPointM => GeometryType::MultiPoint,
        ShapeType::MultiPatch => return None,
    };

    let coordinates = match record.shape {
        Shape::Null => return None,
        Shape::Point(p) => GeometryCoords::Point(Position {
            longitude: p.x.into(),
            latitude: p.y.into(),
            altitude: None
        }),
        Shape::MultiPoint { bbox, num_points, points } => convert_multi_point(points),
        Shape::PolyLine { bbox, num_parts, num_points, parts, points } => convert_polyline(num_parts, num_points, parts, points)?,
        Shape::Polygon { bbox, num_parts, num_points, parts, points } => convert_polygon(num_parts, num_points, parts, points)?,
        Shape::PointM { x, y, m } => GeometryCoords::Point(Position {
            longitude: x.into(),
            latitude: y.into(),
            altitude: None
        }),
        Shape::MultiPointM { bbox, num_points, points, m_range, m_array } => convert_multi_point(points),
        Shape::PolyLineM { bbox, num_parts, num_points, parts, points, m_range, m_array } => convert_polyline(num_parts, num_points, parts, points)?,
        Shape::PolygonM { bbox, num_parts, num_points, parts, points, m_range, m_array } => convert_polygon(num_parts, num_points, parts, points)?,
        Shape::PointZ { x, y, z, m } => {
            let z = match z {
                lector_esri::Double::Data(z) => Some(z),
                lector_esri::Double::NoData => None,
            };

            GeometryCoords::Point(Position {
                longitude: x.into(),
                latitude: y.into(),
                altitude: z
            })
        },
        Shape::MultiPointZ { bbox, num_points, points, z_range, z_array, m_range, m_array } => convert_multi_point(points), // TODO: Altitude
        Shape::PolyLineZ { bbox, num_parts, num_points, parts, points, z_range, z_array, m_range, m_array } => convert_polyline(num_parts, num_points, parts, points)?, // TODO: Altitude
        Shape::PolygonZ { bbox, num_parts, num_points, parts, points, z_range, z_array, m_range, m_array } => convert_polygon(num_parts, num_points, parts, points)?, // TODO: Altitude
        Shape::MultiPatch { bbox, num_parts, num_points, parts, part_types, points, z_range, z_array, m_range, m_array } => todo!(),
    };

    Some(Object::from_iter::<Vec<(_, JsonValue)>>(vec![
        ("type", geometry_type.into()),
        ("coordinates", coordinates.into())
    ]))
}

fn convert_multi_point(points: Vec<Point>) -> GeometryCoords{
    GeometryCoords::MultiPoint(points.into_iter().map(|point| Position {
        longitude: point.x.into(),
        latitude: point.y.into(),
        altitude: None
    }).collect())
}

fn convert_polyline(num_parts: i32, num_points: i32, parts: Vec<i32>, points: Vec<Point>) -> Option<GeometryCoords> {
    let mut parts_v = read_parts(num_parts, num_points, parts, points)?;
    if parts_v.len() == 1 {
        Some(GeometryCoords::LineString(LineString(parts_v.pop().unwrap())))
    } else {
        let parts_v = parts_v.into_iter()
            .map(|points| LineString(points))
            .collect();
        Some(GeometryCoords::MultiLineString(parts_v))
    }
}

fn convert_polygon(num_parts: i32, num_points: i32, parts: Vec<i32>, points: Vec<Point>) -> Option<GeometryCoords>{
    let mut parts_v = read_parts(num_parts, num_points, parts, points)?;

    let parts_v = parts_v.into_iter()
        .map(|points| LinearRing(LineString(points)))
        .collect();
    Some(GeometryCoords::Polygon(parts_v))
}

fn read_parts(num_parts: i32, num_points: i32, parts: Vec<i32>, points: Vec<Point>) -> Option<Vec<Vec<Position>>> {
    let mut part_iter = parts.into_iter();
    let first_part = part_iter.next().unwrap();
    if first_part != 0 {
        eprintln!("La primera parte debe empezar en el primer punto");
        return None
    }
    let mut next_part = part_iter.next();
    let mut parts_v = Vec::new();
    let mut points_v = Vec::new();
    for point_i in 0..num_points {
        if let Some(next) = next_part {
            if point_i >= next {
                let mut new_points_v = vec![];
                std::mem::swap(&mut points_v, &mut new_points_v);

                parts_v.push(new_points_v);
                next_part = part_iter.next()
            }
        }

        let point = points.get(point_i as usize).unwrap();
        points_v.push(point.into())
    };

    parts_v.push(points_v);

    Some(parts_v)
}

enum GeometryType {
    Point,
    LineString,
    Polygon,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
    GeometryCollection
}

impl Into<JsonValue> for GeometryType {
    fn into(self) -> JsonValue {
        match self {
            GeometryType::Point => "Point",
            GeometryType::LineString => "LineString",
            GeometryType::Polygon => "Polygon",
            GeometryType::MultiPoint => "MultiPoint",
            GeometryType::MultiLineString => "MultiLineString",
            GeometryType::MultiPolygon => "MultiPolygon",
            GeometryType::GeometryCollection => "GeometryCollection",
        }.into()
    }
}

struct Position {
    longitude: f64,
    latitude: f64,
    altitude: Option<f64>
}

impl Into<JsonValue> for Position {
    fn into(self) -> JsonValue {
        let mut coords = vec![
            JsonValue::Number(self.longitude.into()),
            JsonValue::Number(self.latitude.into()),
        ];
        if let Some(altitude) = self.altitude {
            coords.push(JsonValue::Number(altitude.into()))
        }

        JsonValue::Array(coords)
    }
}

impl From<&Point> for Position {
    fn from(value: &Point) -> Self {
        let Point {
            x,
            y,
        } = value;
        Position {
            longitude: (*x).into(),
            latitude: (*y).into(),
            altitude: None
        }
    }
}

struct LineString(Vec<Position>);

impl Into<JsonValue> for LineString {
    fn into(self) -> JsonValue {
        JsonValue::Array(self.0.into_iter()
            .map(|pos| pos.into())
            .collect()
        )
    }
}

struct LinearRing(LineString);

impl Into<JsonValue> for LinearRing {
    fn into(self) -> JsonValue {
        self.0.into()
    }
}

struct Polygon(Vec<LineString>);

impl Into<JsonValue> for Polygon {
    fn into(self) -> JsonValue {
        JsonValue::Array(self.0.into_iter()
            .map(|ring| ring.into())
            .collect()
        )
    }
}

enum GeometryCoords {
    Point(Position),
    LineString(LineString),
    Polygon(Vec<LinearRing>),
    MultiPoint(Vec<Position>),
    MultiLineString(Vec<LineString>),
    MultiPolygon(Vec<Polygon>),
    GeometryCollection // UNSUPPORTED
}

impl Into<JsonValue> for GeometryCoords {
    fn into(self) -> JsonValue {
        match self {
            GeometryCoords::Point(p) => p.into(),
            GeometryCoords::LineString(ls) => ls.into(),
            GeometryCoords::Polygon(p) => p.into(),
            GeometryCoords::MultiPoint(mp) => mp.into(),
            GeometryCoords::MultiLineString(mls) => mls.into(),
            GeometryCoords::MultiPolygon(mp) => mp.into(),
            GeometryCoords::GeometryCollection => unimplemented!(),
        }
    }
}
