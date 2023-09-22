use crate::{Double, Integer, Reader, Error};

#[repr(i32)]
enum ShapeType {
    Null = 0,
    Point = 1,
    PolyLine = 3,
    Polygon = 5,
    MultiPoint = 8,
    PointZ = 11,
    PolyLineZ = 13,
    PolygonZ = 15,
    MultiPointZ = 18,
    PointM = 21,
    PolyLineM = 23,
    PolygonM = 25,
    MultiPointM = 28,
    MultiPatch = 32,
}

trait TryRead {
    fn read(buffer: &[u8], cursor: &mut usize) -> Option<Self> where Self: Sized;
}

impl TryFrom<Integer> for ShapeType {
    type Error=Error;

    fn try_from(value: Integer) -> Result<Self, Self::Error> {
        Ok(match value {
            0 => ShapeType::Null,
            1 => ShapeType::Point,
            3 => ShapeType::PolyLine,
            5 => ShapeType::Polygon,
            8 => ShapeType::MultiPoint,
            11 => ShapeType::PointZ,
            13 => ShapeType::PolyLineZ,
            15 => ShapeType::PolygonZ,
            18 => ShapeType::MultiPointZ,
            21 => ShapeType::PointM,
            23 => ShapeType::PolyLineM,
            25 => ShapeType::PolygonM,
            28 => ShapeType::MultiPointM,
            32 => ShapeType::MultiPatch,
            _ => Err(Error::Other)?,
        })
    }
}

impl TryRead for ShapeType {
    fn read(buffer: &[u8], cursor: &mut usize) -> Option<Self> where Self: Sized {
        Integer::read(buffer, cursor).try_into().ok()
    }
}


#[repr(i32)]
enum PartType {
    TriangleStrip = 0,
    TriangleFan = 1,
    OuterRing = 2,
    InnerRing = 3,
    FirstRing = 4,
    Ring = 5,
}

type BoundingBox = [Double;4];

struct Point {
    x: Double,
    y: Double
}

enum Shape {
    Null,
    Point(Point),
    MultiPoint {
        bbox: BoundingBox,
        num_points: Integer,
        points: Vec<Point>
    },
    PolyLine {
        bbox: BoundingBox,
        num_parts: Integer,
        num_points: Integer,
        parts: Vec<Integer>,
        points: Vec<Point>
    },
    Polygon {
        bbox: BoundingBox,
        num_parts: Integer,
        num_points: Integer,
        parts: Vec<Integer>,
        points: Vec<Point>
    },
    PointM {
        x: Double,
        y: Double,
        m: Double
    },
    MultiPointM {
        bbox: BoundingBox,
        num_points: Integer,
        points: Vec<Point>,
        m_range: [Double;2],
        m_array: Vec<Double>
    },
    PolyLineM {
        bbox: BoundingBox,
        num_parts: Integer,
        num_points: Integer,
        parts: Vec<Integer>,
        points: Vec<Point>,
        m_range: [Double;2],
        m_array: Vec<Double>
    },
    PolygonM {
        bbox: BoundingBox,
        num_parts: Integer,
        num_points: Integer,
        parts: Vec<Integer>,
        points: Vec<Point>,
        m_range: [Double;2],
        m_array: Vec<Double>
    },
    PointZ {
        x: Double,
        y: Double,
        z: Double,
        m: Double
    },
    MultiPointZ {
        bbox: BoundingBox,
        num_points: Integer,
        points: Vec<Point>,
        z_range: [Double;2],
        z_array: Vec<Double>,
        m_range: [Double;2],
        m_array: Vec<Double>
    },
    PolyLineZ {
        bbox: BoundingBox,
        num_parts: Integer,
        num_points: Integer,
        parts: Vec<Integer>,
        points: Vec<Point>,
        z_range: [Double;2],
        z_array: Vec<Double>,
        m_range: [Double;2],
        m_array: Vec<Double>
    },
    PolygonZ {
        bbox: BoundingBox,
        num_parts: Integer,
        num_points: Integer,
        parts: Vec<Integer>,
        points: Vec<Point>,
        z_range: [Double;2],
        z_array: Vec<Double>,
        m_range: [Double;2],
        m_array: Vec<Double>
    },
    MultiPatch {
        bbox: BoundingBox,
        num_parts: Integer,
        num_points: Integer,
        parts: Vec<Integer>,
        part_types: Vec<PartType>,
        points: Vec<Point>,
        z_range: [Double;2],
        z_array: Vec<Double>,
        m_range: [Double;2],
        m_array: Vec<Double>
    }
}

struct Record {
    record_number: Integer,
    content_length: Integer,
    shape_type: ShapeType,
    shape: Shape
}

impl TryRead for Record {
    fn read(buffer: &[u8], cursor: &mut usize) -> Option<Self> where Self: Sized {
        todo!()
    }
}

pub(crate) fn read_shapefile(shapefile: &[u8]) {
    let mut cursor = 0;
    let header = Header::read(shapefile, &mut cursor);
    let bytes_totales = shapefile.len();
    if let Some(header) = header {
        if bytes_totales != (header.file_length * 2) as usize {
            // file_length mide en palabras de 16 bits, por lo tanto los bytes es el doble
            eprintln!("La longitud del fichero no se correspondo a lo especificado en la cabecera")
        }
    };

    let mut records = Vec::new();
    while cursor < bytes_totales {

    }
}

struct Header {
    magic: Integer,
    file_length: Integer,
    version: Integer,
    shape_type: ShapeType,
    bb_xmin: Double,
    bb_ymin: Double,
    bb_xmax: Double,
    bb_ymax: Double,
    bb_zmin: Double,
    bb_zmax: Double,
    bb_mmin: Double,
    bb_mmax: Double,
}

impl TryRead for Header {
    /// Lee los 100 bytes del header aunque falle.
    fn read(buffer: &[u8], cursor: &mut usize) -> Option<Self> where Self: Sized {
        let mut failed = false;

        let magic = Integer::read_be(buffer, cursor);
        if magic != 9994 {
            failed = true;
            eprintln!("Numero mágico incorrecto")
        }
        for _ in 0..5 {
            // padding (20 bytes)
            // 5 * 4 = 20. (cada Integer 4 bytes)
            Integer::read(buffer, cursor);
        }

        let file_length = Integer::read_be(buffer, cursor);
        let version = Integer::read(buffer, cursor);
        if version != 1000 {
            failed = true;
            eprintln!("Versión incorrecta")
        }

        let shape_type = ShapeType::read(buffer, cursor);
        let bb_xmin = Double::read(buffer, cursor);
        let bb_ymin = Double::read(buffer, cursor);
        let bb_xmax = Double::read(buffer, cursor);
        let bb_ymax = Double::read(buffer, cursor);
        let bb_zmin = Double::read(buffer, cursor);
        let bb_zmax = Double::read(buffer, cursor);
        let bb_mmin = Double::read(buffer, cursor);
        let bb_mmax = Double::read(buffer, cursor);
        // Se han leido los 100 bytes del header

        // sacamos el ShapeType de Option<ShapeType> después de haber leido los 100 bytes
        let shape_type = shape_type?;
        if failed {
            return None
        }
        Some(Header {
            magic,
            file_length,
            version,
            shape_type,
            bb_xmin,
            bb_ymin,
            bb_xmax,
            bb_ymax,
            bb_zmin,
            bb_zmax,
            bb_mmin,
            bb_mmax,
        })
    }
}
