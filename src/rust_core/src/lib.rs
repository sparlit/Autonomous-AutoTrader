use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn validate_swing_setup_fast(h4_trend: i32, d1_trend: i32, current_rsi: f64) -> PyResult<bool> {
    // Magic: 90001
    if h4_trend == 0 || d1_trend == 0 { return Ok(false); }
    if h4_trend != d1_trend { return Ok(false); }
    if h4_trend == 1 && current_rsi > 75.0 { return Ok(false); }
    if h4_trend == -1 && current_rsi < 25.0 { return Ok(false); }
    Ok(true)
}

#[pyfunction]
fn calculate_var_parallel(exposure_list: Vec<f64>, vol_list: Vec<f64>) -> PyResult<f64> {
    // Magic: 90002
    if exposure_list.len() != vol_list.len() {
        return Ok(0.0);
    }

    let total_risk: f64 = exposure_list.par_iter()
        .zip(vol_list.par_iter())
        .map(|(exp, vol)| exp.abs() * vol * 1.645)
        .sum();

    Ok(total_risk)
}

#[pyfunction]
fn calculate_position_size_v3(equity: f64, risk_pct: f64, sl_pts: f64, tick_val: f64, tick_size: f64) -> PyResult<f64> {
    // Magic: 90003
    if sl_pts <= 0.0 || tick_val <= 0.0 || tick_size <= 0.0 { return Ok(0.0); }
    let risk_amount = equity * (risk_pct / 100.0);
    let num_ticks = sl_pts / tick_size;
    let lots = risk_amount / (num_ticks * tick_val);
    Ok(lots)
}

#[pymodule]
fn aat_rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(validate_swing_setup_fast, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_var_parallel, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_position_size_v3, m)?)?;
    Ok(())
}
