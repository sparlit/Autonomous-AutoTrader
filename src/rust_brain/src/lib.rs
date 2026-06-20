use pyo3::prelude::*;

#[pyfunction]
fn validate_signal_fast(direction: i32, confidence: f64) -> PyResult<bool> {
    // Zero-Tolerance Institutional Veto Logic (Rust-speed)
    // Magic: 9001
    if direction == 0 { return Ok(false); }
    if confidence < 0.6 { return Ok(false); }
    Ok(true)
}

#[pymodule]
fn aat_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(validate_signal_fast, m)?)?;
    Ok(())
}
