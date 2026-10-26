"""Check the CT method table's shape and its agreement with the manifest."""

import json
from pathlib import Path

CRS_DIR = Path(__file__).parent.parent / "crs"
TABLE = json.loads((CRS_DIR / "geotiff-ct-methods.json").read_text())
MANIFEST = json.loads((CRS_DIR / "manifest.json").read_text())
KINDS = {"angular", "linear", "scale", "azimuth"}
RULE_KEYS = {"present", "abs_value", "value", "any", "all"}
SCALE_AND_AZIMUTH_KEYS = ["ProjScaleAtNatOrigin", "ProjScaleAtCenter", "ProjAzimuthAngle"]


def _rule_ok(rule: dict) -> bool:
    ((key, body),) = rule.items()
    if key in ("any", "all"):
        return all(_rule_ok(r) for r in body)
    if key == "present":
        return isinstance(body, str)
    return key in RULE_KEYS and set(body) == {"param", "equals"}


def test_table_covers_every_ct_code():
    assert set(TABLE["methods"]) == {str(c) for c in range(1, 29)} | {"9815"}
    assert {c for c, m in TABLE["methods"].items() if "unsupported" in m} == {"2", "5", "6"}


def test_variants_are_well_formed():
    allowed_keys = (
        TABLE["units"]["angular_keys"] + TABLE["units"]["linear_keys"] + SCALE_AND_AZIMUTH_KEYS
    )
    for method in TABLE["methods"].values():
        if "unsupported" in method:
            assert set(method) == {"ct_name", "unsupported"}
            continue
        assert "libgeotiff" in method
        variants = method["variants"]
        assert "when" not in variants[-1]
        for v in variants[:-1]:
            assert _rule_ok(v["when"])
        for v in variants:
            if "unrepresentable" in v:
                continue
            assert set(v["method"]) == {"name", "epsg", "proj"}
            for p in v["parameters"]:
                assert set(p) >= {"name", "epsg", "proj", "kind", "keys", "default"}
                assert p["kind"] in KINDS
                assert p["keys"] and all(k in allowed_keys for k in p["keys"])
            assert v.get("axes", ["east", "north"]) in (["east", "north"], ["west", "south"])
            assert "gdal" in v


def test_variant_rules():
    assert TABLE["methods"]["7"]["variants"][0]["when"] == {"present": "ProjStdParallel1"}
    assert TABLE["methods"]["15"]["variants"][0]["when"] == {
        "value": {"param": "Scale factor at natural origin", "equals": 1}
    }
    assert TABLE["methods"]["15"]["variants"][1]["when"] == {
        "abs_value": {"param": "Latitude of natural origin", "equals": 90}
    }
    assert "unrepresentable" in TABLE["methods"]["15"]["variants"][2]
    assert TABLE["methods"]["27"]["variants"][0]["axes"] == ["west", "south"]


def test_every_supported_method_has_a_fixture():
    seen = {str(c["geokeys"].get("ProjCoordTrans")) for c in MANIFEST["cases"]}
    for code, method in TABLE["methods"].items():
        if "unsupported" not in method:
            assert code in seen, code


def test_every_fixture_ct_code_is_in_table():
    for c in MANIFEST["cases"]:
        ct = c["geokeys"].get("ProjCoordTrans")
        if ct is not None:
            assert str(ct) in TABLE["methods"], c["name"]


def test_table_method_names_match_manifest():
    """For every tested fixture with a CT code, GDAL's method is one of the table's variants."""
    for c in MANIFEST["cases"]:
        ct = c["geokeys"].get("ProjCoordTrans")
        if ct is None or c["gdal"]["proj4"] is None:
            continue
        variants = TABLE["methods"][str(ct)]["variants"]
        names = {v["method"]["name"] for v in variants if "method" in v}
        assert c["core"]["method"]["name"] in names, (c["name"], c["core"]["method"]["name"])
