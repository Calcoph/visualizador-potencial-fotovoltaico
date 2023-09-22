use std::{path::Path, io::Error as IoError};

use dbase::Error as DBError;

mod shape_file;
mod index_file;

trait Reader {
    fn read(buffer: &[u8], cursor: &mut usize) -> Self;
    fn read_be(buffer: &[u8], cursor: &mut usize) -> Self;
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
}

enum Double {
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

enum Error {
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

fn read(shape_file_path: &Path, index_file_path: &Path, dbase_file_path: &Path) -> Result<(), Error> {
    let index_file = std::fs::read(shape_file_path)?;
    //index_file = std::fs::read(index_file_path);
    dbase::read(dbase_file_path)?;

    Ok(())
}
