use pyo3::prelude::*;
use rayon::prelude::*;
use rust_decimal::prelude::*;
use rust_decimal_macros::dec;
use hashbrown::HashMap;
use parking_lot::RwLock;
use std::sync::Arc;

// --- AAT Institutional Core (Consolidated) ---
// Magic Numbers: 90xxx (Logic), 91xxx (Infrastructure), 92xxx (Risk)

// FROM aat_rust_core
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

// FROM aat_heavy (Integrated as class)
#[pyclass]
pub struct HeavyEngine {
    order_book: Arc<RwLock<HashMap<String, f64>>>,
}

#[pymethods]
impl HeavyEngine {
    #[new]
    fn new() -> Self {
        // Magic: 91001
        Self {
            order_book: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    fn update_price(&self, symbol: String, price: f64) {
        // Magic: 91002
        let mut book = self.order_book.write();
        book.insert(symbol, price);
    }

    fn check_risk_decimal(&self, equity: f64, risk_pct: f64, sl_dist: f64) -> PyResult<bool> {
        // Magic: 92001 - Institutional Pre-Trade Risk via rust_decimal
        let e = Decimal::from_f64(equity).unwrap_or(dec!(0));
        let r = Decimal::from_f64(risk_pct).unwrap_or(dec!(0));
        let s = Decimal::from_f64(sl_dist).unwrap_or(dec!(0));

        if e <= dec!(0) || r <= dec!(0) || s <= dec!(0) { return Ok(false); }

        let risk_val = e * (r / dec!(100));
        if risk_val > dec!(1000) { return Ok(false); }

        Ok(true)
    }
}

// FROM aat_rust (Orphan function, included for completeness)
#[pyfunction]
fn validate_signal_fast(direction: i32, confidence: f64) -> PyResult<bool> {
    // Magic: 90004
    if direction == 0 { return Ok(false); }
    if confidence < 0.6 { return Ok(false); }
    Ok(true)
}

#[pymodule]
fn aat_institutional_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(validate_swing_setup_fast, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_var_parallel, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_position_size_v3, m)?)?;
    m.add_function(wrap_pyfunction!(validate_signal_fast, m)?)?;
    m.add_class::<HeavyEngine>()?;
    Ok(())
}
