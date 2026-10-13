"""Reference Mendelian genotype crosses and input validation."""
import pytest
from inheritance import calculate_recurrence_risk as risk


def test_autosomal_dominant_heterozygote():
    result = risk("autosomal_dominant", "Aa", "aa")
    assert result["risk"]["overall"]["affected"] == 0.5
    assert result["genotypes"]["sons"] == {"Aa": 0.5, "aa": 0.5}


def test_autosomal_recessive_two_carriers():
    result = risk("autosomal_recessive", "Aa", "Aa")
    assert result["risk"]["overall"] == {
        "affected": 0.25, "unaffected_carrier": 0.5, "unaffected_noncarrier": 0.25}


def test_x_recessive_maternal_carrier():
    result = risk("x_linked_recessive", "XAXa", "XAY")
    assert result["risk"]["sons"]["affected"] == 0.5
    assert result["risk"]["daughters"]["affected"] == 0
    assert result["risk"]["daughters"]["unaffected_carrier"] == 0.5
    assert result["risk"]["overall"]["affected"] == 0.25


def test_x_dominant_paternal_variant():
    result = risk("x_linked_dominant", "XAXA", "XaY")
    assert result["risk"]["daughters"]["affected"] == 1
    assert result["risk"]["sons"]["affected"] == 0


def test_complete_homozygous_cross():
    assert risk("autosomal_recessive", "aa", "AA")["risk"]["overall"]["unaffected_carrier"] == 1


@pytest.mark.parametrize("args", [
    ("other", "Aa", "aa"),
    ("autosomal_dominant", "XAXa", "aa"),
    ("x_linked_recessive", "XAY", "XAXa"),
    ("x_linked_dominant", "XAXa", "aa"),
])
def test_invalid_genotypes(args):
    with pytest.raises(ValueError):
        risk(*args)


@pytest.mark.parametrize("mode,mom,dad", [
    ("autosomal_dominant", "Aa", "Aa"),
    ("autosomal_recessive", "aa", "Aa"),
    ("x_linked_recessive", "XaXa", "XaY"),
    ("x_linked_dominant", "XAXa", "XaY"),
])
def test_probabilities_sum_to_one(mode, mom, dad):
    res = risk(mode, mom, dad)
    for sex in ("sons", "daughters", "overall"):
        assert sum(res["risk"][sex].values()) == pytest.approx(1)
    for sex in ("sons", "daughters"):
        assert sum(res["genotypes"][sex].values()) == pytest.approx(1)


def test_batch_csv_exports_scalar_probabilities(tmp_path):
    import csv
    from pedigree import process_csv
    source = tmp_path / "cases.csv"
    output = tmp_path / "results.csv"
    source.write_text(
        "case_id,inheritance,mother,father\n"
        "case1,autosomal_recessive,Aa,Aa\n",
        encoding="utf-8"
    )
    process_csv(str(source), str(output))
    with output.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 1
    assert rows[0]["risk_affected_overall"] == "0.25"
    assert rows[0]["risk_unaffected_carrier_overall"] == "0.5"
    assert rows[0]["genotypes_sons"] == '{"AA": 0.25, "Aa": 0.5, "aa": 0.25}'
