type Integer = i32;

enum Double {
    Data(f64),
    NoData
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

fn main() {
    let min = -10_f64.powi(38);
    dbg!(min);
}
