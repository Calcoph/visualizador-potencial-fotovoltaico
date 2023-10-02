use std::{path::Path, io::{Error as IoError, Cursor}};

use dbase::{Error as DBError, Record as DBRecord};
pub use shape_file::{Record, Shape, ShapeType, Point};
use shape_file::read_shapefile;

mod shape_file;
mod index_file;

trait Reader {
    fn read(buffer: &[u8], cursor: &mut usize) -> Self;
    fn read_be(buffer: &[u8], cursor: &mut usize) -> Self;
    fn return_cursor(cursor: &mut usize);
}

type Integer = i32;

impl Reader for Integer {
    fn read(buffer: &[u8], cursor: &mut usize) -> Self {
        *cursor += 4;
        i32::from_le_bytes([
            buffer[*cursor-4],
            buffer[*cursor-3],
            buffer[*cursor-2],
            buffer[*cursor-1]
        ])
    }

    fn read_be(buffer: &[u8], cursor: &mut usize) -> Self {
        *cursor += 4;
        i32::from_be_bytes([
            buffer[*cursor-4],
            buffer[*cursor-3],
            buffer[*cursor-2],
            buffer[*cursor-1]
        ])
    }

    fn return_cursor(cursor: &mut usize) {
        *cursor -= 4;
    }
}

#[derive(Debug, Clone, Copy)]
pub enum Double {
    Data(f64),
    NoData
}

impl Reader for Double {
    fn read(buffer: &[u8], cursor: &mut usize) -> Self {
        *cursor += 8;
        f64::from_le_bytes([
            buffer[*cursor-8],
            buffer[*cursor-7],
            buffer[*cursor-6],
            buffer[*cursor-5],
            buffer[*cursor-4],
            buffer[*cursor-3],
            buffer[*cursor-2],
            buffer[*cursor-1]
        ]).into()
    }

    fn read_be(buffer: &[u8], cursor: &mut usize) -> Self {
        *cursor += 8;
        f64::from_be_bytes([
            buffer[*cursor-8],
            buffer[*cursor-7],
            buffer[*cursor-6],
            buffer[*cursor-5],
            buffer[*cursor-4],
            buffer[*cursor-3],
            buffer[*cursor-2],
            buffer[*cursor-1]
        ]).into()
    }

    fn return_cursor(cursor: &mut usize) {
        *cursor -= 8;
    }
}

const DOUBLE_DATA_THRESHOLD: f64 = -1e38;

impl From<f64> for Double {
    fn from(double: f64) -> Self {
        if double < DOUBLE_DATA_THRESHOLD {
            Double::NoData
        } else {
            Double::Data(double)
        }
    }
}

impl Into<f64> for Double {
    fn into(self) -> f64 {
        match self {
            Double::Data(data) => data,
            Double::NoData => DOUBLE_DATA_THRESHOLD,
        }
    }
}

#[derive(Debug)]
pub enum Error {
    Io(IoError),
    DBase(DBError),
    Other
}

impl From<DBError> for Error {
    fn from(value: DBError) -> Self {
        Error::DBase(value)
    }
}

impl From<IoError> for Error {
    fn from(value: IoError) -> Self {
        Error::Io(value)
    }
}

pub fn read(shape_file_path: &Path, index_file_path: &Path, dbase_file_path: &Path) -> Result<Vec<Option<Record>>, Error> {
    let shape_file = std::fs::read(shape_file_path)?;
    let index_file = std::fs::read(index_file_path)?;
    let dbase_bytes = std::fs::read(dbase_file_path);

    let shapes = read_shapefile(&shape_file);

    Ok(shapes)
}

pub fn read_bytes(shape_file: &[u8], index_file: &[u8], dbase_file: &[u8]) -> Result<Vec<Option<Record>>, Error> {
    let shapes = read_shapefile(shape_file);

    let dbase_file = Cursor::new(dbase_file);
    let dbase_records = dbase::Reader::new(dbase_file);

    Ok(shapes)
}
