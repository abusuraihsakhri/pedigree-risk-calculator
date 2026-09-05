"""Tests for the core pedigree calculation module."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pytest
import pedigree as m


def test_smoke():
    r = m.assess_row({'value': 10})
    assert isinstance(r, dict)


def test_calculate_score_basic():
    result = m.calculate_score(a=5, b=10)
    assert "score" in result
    assert "inputs" in result
    assert result["inputs"] == 2


def test_calculate_score_empty():
    result = m.calculate_score()
    assert "score" in result
    assert result["inputs"] == 1  # uses default value


def test_calculate_score_with_strings():
    result = m.calculate_score(x="3.5", y="2.1")
    assert result["inputs"] == 2
    assert result["score"] > 0


def test_meld_na_calculation():
    result = m.calculate_meld_na(bilirubin=2.5, creatinine=1.2, inr=1.5, sodium=135)
    assert "meld_na" in result
    assert "risk_tier" in result
    assert result["risk_tier"] in ["low", "moderate", "high"]


def test_meld_na_with_dialysis():
    result = m.calculate_meld_na(bilirubin=3.0, creatinine=0.8, dialysis=True)
    assert result["meld_na"] >= 6  # minimum MELD score


def test_qtc_calculation():
    result = m.calculate_qtc(qt_ms=420, hr_bpm=72)
    assert "qtc_ms" in result
    assert "prolonged" in result
    assert isinstance(result["prolonged"], bool)


def test_qtc_with_rr():
    result = m.calculate_qtc(qt_ms=400, rr_ms=1000)
    assert result["qtc_ms"] == 400.0  # QTc = QT when RR = 1s


def test_bmi_z_calculation():
    result = m.calculate_bmi_z(weight_kg=70, height_cm=175, age_months=120, sex="M")
    assert "bmi" in result
    assert "z_score" in result
    assert result["bmi"] > 0


def test_hba1c_to_eag():
    result = m.convert_hba1c(hba1c_percent=7.0)
    assert "eag_mgdl" in result
    assert result["hba1c_percent"] == 7.0


def test_eag_to_hba1c():
    result = m.convert_hba1c(eag_mgdl=154)
    assert "hba1c_percent" in result


def test_apri_fib4_calculation():
    result = m.calculate_apri_fib4(ast_u_l=60, alt_u_l=45, platelets_109=180, age_years=50)
    assert "apri" in result
    assert "fib4" in result
    assert "fib4_risk" in result


def test_assess_row_meld():
    row = {"bilirubin": 2.0, "creatinine": 1.1, "inr": 1.3, "sodium": 138}
    result = m.assess_row(row)
    assert "meld_na" in result


def test_assess_row_qt():
    row = {"qt_ms": 450, "hr_bpm": 80}
    result = m.assess_row(row)
    assert "qtc_ms" in result


def test_assess_row_bmi():
    row = {"weight_kg": 60, "height_cm": 165, "age": 96, "sex": "F"}
    result = m.assess_row(row)
    assert "bmi" in result


def test_assess_row_hba1c():
    row = {"hba1c_percent": 8.5}
    result = m.assess_row(row)
    assert "eag_mgdl" in result


def test_assess_row_apri():
    row = {"ast_u_l": 75, "alt_u_l": 50, "platelets_109": 150}
    result = m.assess_row(row)
    assert "apri" in result
    assert "fib4" in result


def test_assess_row_invalid_input():
    result = m.assess_row("not a dict")
    assert "error" in result


def test_safe_float_none():
    assert m._safe_float(None) == 0.0


def test_safe_float_valid():
    assert m._safe_float("3.14") == 3.14


def test_safe_float_invalid():
    assert m._safe_float("abc", default=1.0) == 1.0
