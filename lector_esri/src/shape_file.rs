use crate::{Double, Integer, Reader, Error};

#[repr(i32)]
#[derive(Debug, Clone, Copy)]
pub enum ShapeType {
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
    fn return_cursor(cursor: &mut usize);
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

    fn return_cursor(cursor: &mut usize) {
        Integer::return_cursor(cursor)
    }
}


#[repr(i32)]
#[derive(Debug)]
pub enum PartType {
    TriangleStrip = 0,
    TriangleFan = 1,
    OuterRing = 2,
    InnerRing = 3,
    FirstRing = 4,
    Ring = 5,
}

impl PartType {
    fn read(buffer: &[u8], cursor: &mut usize) -> Option<Self> {
        Some(match Integer::read(buffer, cursor) {
            0 => Self::TriangleStrip,
            1 => Self::TriangleFan,
            2 => Self::OuterRing,
            3 => Self::InnerRing,
            4 => Self::FirstRing,
            5 => Self::Ring,
            _ => {
                eprintln!(r#"Uno de los "PartType" tiene un valor incorrecto, no se ha podido leer"#);
                return None
            }
        })
    }
}

type BoundingBox = [Double;4];

impl Reader for BoundingBox {
    fn read(buffer: &[u8], cursor: &mut usize) -> Self {
        let a = Double::read(buffer, cursor);
        let b = Double::read(buffer, cursor);
        let c = Double::read(buffer, cursor);
        let d = Double::read(buffer, cursor);

        [a,b,c,d]
    }

    fn read_be(buffer: &[u8], cursor: &mut usize) -> Self {
        let a = Double::read_be(buffer, cursor);
        let b = Double::read_be(buffer, cursor);
        let c = Double::read_be(buffer, cursor);
        let d = Double::read_be(buffer, cursor);

        [a,b,c,d]
    }

    fn return_cursor(cursor: &mut usize) {
        Double::return_cursor(cursor);
        Double::return_cursor(cursor);
        Double::return_cursor(cursor);
        Double::return_cursor(cursor);
    }
}

#[derive(Debug, Clone, Copy)]
pub struct Point {        
    pub x: Double,
    pub y: Double
}

impl Point {
    fn read(buffer: &[u8], cursor: &mut usize) -> Self {
        let x = Double::read(buffer, cursor);
        let y = Double::read(buffer, cursor);

        Point { x, y }
    }
}

#[derive(Debug)]
pub enum Shape {
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
        part_types: Vec<Option<PartType>>,
        points: Vec<Point>,
        z_range: [Double;2],
        z_array: Vec<Double>,
        m_range: [Double;2],
        m_array: Vec<Double>
    }
}

#[derive(Debug)]
pub struct Record {
    record_number: Integer,
    content_length: Integer,
    pub shape_type: ShapeType,
    pub shape: Shape
}

impl Shape {
    fn read(buffer: &[u8], cursor: &mut usize, shape_type: ShapeType) -> Self {
        match shape_type {
            ShapeType::Null => Shape::Null,
            ShapeType::Point => {
                Shape::Point(Point::read(buffer, cursor))
            },
            ShapeType::PolyLine => {
                let PolygonAttrs {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points
                } = PolygonAttrs::read(buffer, cursor);

                Shape::PolyLine {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points
                }
            },
            ShapeType::Polygon => {
                let PolygonAttrs {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points
                } = PolygonAttrs::read(buffer, cursor);

                Shape::Polygon {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points
                }
            },
            ShapeType::MultiPoint => {
                let MultiPointAttrs {
                    bbox,
                    num_points,
                    points
                } = MultiPointAttrs::read(buffer, cursor);

                Shape::MultiPoint {
                    bbox,
                    num_points,
                    points
                }
            },
            ShapeType::PointZ => {
                let x = Double::read(buffer, cursor);
                let y = Double::read(buffer, cursor);
                let z = Double::read(buffer, cursor);
                let m = Double::read(buffer, cursor);

                Shape::PointZ {
                    x,
                    y,
                    z,
                    m,
                }
            },
            ShapeType::PolyLineZ => {
                let PolygonAttrs {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points
                } = PolygonAttrs::read(buffer, cursor);
                let (z_range, z_array) = read_z(buffer, cursor, num_points);
                let (m_range, m_array) = read_z(buffer, cursor, num_points);

                Shape::PolyLineZ {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points,
                    z_range,
                    z_array,
                    m_range,
                    m_array,
                }
            },
            ShapeType::PolygonZ => {
                let PolygonAttrs {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points
                } = PolygonAttrs::read(buffer, cursor);
                let (z_range, z_array) = read_z(buffer, cursor, num_points);
                let (m_range, m_array) = read_z(buffer, cursor, num_points);

                Shape::PolygonZ {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points,
                    z_range,
                    z_array,
                    m_range,
                    m_array,
                }
            },
            ShapeType::MultiPointZ => {
                let MultiPointAttrs {
                    bbox,
                    num_points,
                    points
                } = MultiPointAttrs::read(buffer, cursor);
                let (z_range, z_array) = read_z(buffer, cursor, num_points);
                let (m_range, m_array) = read_z(buffer, cursor, num_points);

                Shape::MultiPointZ {
                    bbox,
                    num_points,
                    points,
                    z_range,
                    z_array,
                    m_range,
                    m_array,
                }
            },
            ShapeType::PointM => {
                let x = Double::read(buffer, cursor);
                let y = Double::read(buffer, cursor);
                let m = Double::read(buffer, cursor);

                Shape::PointM {
                    x,
                    y,
                    m,
                }  
            },
            ShapeType::PolyLineM => {
                let PolygonAttrs {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points
                } = PolygonAttrs::read(buffer, cursor);
                let (m_range, m_array) = read_z(buffer, cursor, num_points);

                Shape::PolyLineM {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points,
                    m_range,
                    m_array,
                }
            },
            ShapeType::PolygonM => {
                let PolygonAttrs {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points
                } = PolygonAttrs::read(buffer, cursor);
                let (m_range, m_array) = read_z(buffer, cursor, num_points);

                Shape::PolygonM {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    points,
                    m_range,
                    m_array,
                }
            },
            ShapeType::MultiPointM => {
                let MultiPointAttrs {
                    bbox,
                    num_points,
                    points
                } = MultiPointAttrs::read(buffer, cursor);
                let (m_range, m_array) = read_z(buffer, cursor, num_points);

                Shape::MultiPointM {
                    bbox,
                    num_points,
                    points,
                    m_range,
                    m_array,
                }
            },
            ShapeType::MultiPatch => {
                let bbox = BoundingBox::read(buffer, cursor);
                let num_parts = Integer::read(buffer, cursor);
                let num_points = Integer::read(buffer, cursor);

                let mut parts = Vec::new();
                for _ in 0..num_parts {
                    parts.push(Integer::read(buffer, cursor))
                }

                let mut part_types = Vec::new();
                for _ in 0..num_parts {
                    part_types.push(PartType::read(buffer, cursor))
                }

                let mut points = Vec::new();
                for _ in 0..num_points {
                    points.push(Point::read(buffer, cursor))
                }
                let (z_range, z_array) = read_z(buffer, cursor, num_points);
                let (m_range, m_array) = read_z(buffer, cursor, num_points);

                Shape::MultiPatch {
                    bbox,
                    num_parts,
                    num_points,
                    parts,
                    part_types,
                    points,
                    z_range,
                    z_array,
                    m_range,
                    m_array
                }
            },
        }
    }
}

impl TryRead for Record {
    fn read(buffer: &[u8], cursor: &mut usize) -> Option<Self> where Self: Sized {
        let record_number = Integer::read_be(buffer, cursor);
        let content_length = Integer::read_be(buffer, cursor);
        let shape_type = ShapeType::read(buffer, cursor).or_else(|| {
            eprintln!(r#"No se ha podido leer un "Record" ya que su "ShapeType" tiene un valor incorrecto"#);
            Integer::return_cursor(cursor);
            Integer::return_cursor(cursor);
            ShapeType::return_cursor(cursor);
            None
        })?;
        let shape = Shape::read(buffer, cursor, shape_type);

        Some(Record {
            record_number,
            content_length,
            shape_type,
            shape,
        })
    }

    // Al fallar de leer un Record se debe avanzar el cursor, no atrasarlo
    fn return_cursor(cursor: &mut usize) {
        unimplemented!()
    }
}

pub(crate) fn read_shapefile(shapefile: &[u8]) -> Vec<Option<Record>> {
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
        records.push(Record::read(shapefile, &mut cursor))
    }

    records
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

    fn return_cursor(cursor: &mut usize) {
        *cursor -= 100;
    }
}

struct PolygonAttrs {
    bbox: BoundingBox,
    num_parts: Integer,
    num_points: Integer,
    parts: Vec<Integer>,
    points: Vec<Point>
}

impl PolygonAttrs {
    fn read(buffer: &[u8], cursor: &mut usize) -> PolygonAttrs {
        let bbox = BoundingBox::read(buffer, cursor);
        let num_parts = Integer::read(buffer, cursor);
        let num_points = Integer::read(buffer, cursor);
    
        let mut parts = Vec::new();
        for _ in 0..num_parts {
            parts.push(Integer::read(buffer, cursor))
        }
    
        let mut points = Vec::new();
        for _ in 0..num_points {
            points.push(Point::read(buffer, cursor))
        }
    
        PolygonAttrs { bbox, num_parts, num_points, parts, points }
    }
}

struct MultiPointAttrs {
    bbox: BoundingBox,
    num_points: Integer,
    points: Vec<Point>
}

impl MultiPointAttrs {
    fn read(buffer: &[u8], cursor: &mut usize) -> Self {
        let bbox = BoundingBox::read(buffer, cursor);
        let num_parts = Integer::read(buffer, cursor);
        let num_points = Integer::read(buffer, cursor);
    
        let mut parts = Vec::new();
        for _ in 0..num_parts {
            parts.push(Integer::read(buffer, cursor))
        }
    
        let mut points = Vec::new();
        for _ in 0..num_points {
            points.push(Point::read(buffer, cursor))
        }
    
        MultiPointAttrs { bbox, num_points, points }   
    }
}

/// Aunque se llame "read_z" también sirve para leer la parte "m" ya que son idénticas
fn read_z(buffer: &[u8], cursor: &mut usize, num_points: Integer) -> ([Double;2], Vec<Double>) {
    let a = Double::read(buffer, cursor);
    let b = Double::read(buffer, cursor);

    let mut z_array = Vec::new();
    for _ in 0..num_points {
        z_array.push(Double::read(buffer, cursor))
    }

    ([a,b], z_array)
}
