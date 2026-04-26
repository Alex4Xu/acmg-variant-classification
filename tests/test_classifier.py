from pathlib import Path
import importlib.util
import json


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "classifier.py"
spec = importlib.util.spec_from_file_location("classifier", MODULE_PATH)
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)


def test_reference_cases_pass():
    cases = json.loads((Path(__file__).resolve().parents[1] / "references" / "test_cases.json").read_text())
    results = classifier.run_tests(cases)
    assert all(r["pass"] for r in results)


def test_3m_3p_is_likely_pathogenic_not_pathogenic():
    got = classifier.classify(
        {"very_strong": 0, "strong": 0, "moderate": 3, "supporting": 3},
        {"standalone": 0, "strong": 0, "supporting": 0},
    )
    assert got == "Likely Pathogenic"


def test_pvs1_plus_one_supporting_is_vus():
    got = classifier.classify(
        {"very_strong": 1, "strong": 0, "moderate": 0, "supporting": 1},
        {"standalone": 0, "strong": 0, "supporting": 0},
    )
    assert got == "VUS"


def test_invalid_counts_raise_value_error():
    bad_inputs = [
        ({"very_strong": -1}, {"standalone": 0}),
        ({"very_strong": 1.5}, {"standalone": 0}),
        ({"very_strong": True}, {"standalone": 0}),
        ({"very_strong": 0}, {"standalone": -1}),
    ]
    for pathogenic, benign in bad_inputs:
        try:
            classifier.classify(pathogenic, benign)
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError not raised for invalid count")
