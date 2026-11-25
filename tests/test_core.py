import copy
import json
from fractions import Fraction as F
from pathlib import Path

import pytest

from markscheme import check_scheme, score
from markscheme.__main__ import main

EX = Path(__file__).resolve().parent.parent / "examples" / "q1.json"
GOOD = json.loads(EX.read_text())


def bad(**change):
    s = copy.deepcopy(GOOD)
    s.update(change)
    return s


def test_example_is_consistent():
    assert check_scheme(GOOD) == []


def test_total_mismatch():
    assert "add to 5 but the total says 6" in " ".join(check_scheme(bad(total=6)))


def test_a_mark_needs_method():
    s = copy.deepcopy(GOOD)
    s["steps"][1]["needs"] = []
    assert any("must need a method" in p for p in check_scheme(s))
    s = copy.deepcopy(GOOD)
    s["steps"][1]["needs"] = ["s3"]  # needs a B step only
    assert any("at least one M" in p for p in check_scheme(s))


def test_forward_and_self_references_and_duplicates():
    s = copy.deepcopy(GOOD)
    s["steps"][0]["needs"] = ["s2"]
    s["steps"][2]["id"] = "s1"
    s["steps"][1]["needs"] = ["s2"]
    text = " ".join(check_scheme(s))
    assert "not an earlier step" in text and "used twice" in text and "cannot need itself" in text


def test_bad_types_and_marks():
    s = copy.deepcopy(GOOD)
    s["steps"][0]["type"] = "X"
    s["steps"][1]["marks"] = 0
    s["steps"][2]["marks"] = "1/2"
    s["steps"][2]["needs"] = ["s1"]
    s["steps"][3]["marks"] = "abc"
    text = " ".join(check_scheme(s))
    for part in ("type must be", "must be positive", "whole number", "not a number", "needs nothing"):
        assert part in text
    assert check_scheme({"steps": []}) == ["the scheme has no steps"]


def test_b_with_follow_through_refused():
    s = copy.deepcopy(GOOD)
    s["steps"][2]["ft"] = True
    assert any("does not apply to a B mark" in p for p in check_scheme(s))


def test_score_full_and_partial():
    assert score(GOOD, ["s1", "s2", "s3", "s4", "s5"]) == (F(5), F(5), [])
    got, mx, notes = score(GOOD, ["s2", "s3"])
    assert (got, mx) == (F(1), F(5))  # s2 needs s1, which was not earned
    assert notes == ["s2 not counted: needs s1"]


def test_follow_through_counts_and_is_flagged():
    got, mx, notes = score(GOOD, ["s1", "s3", "s4", "s5"])  # wrong x: s2 not earned
    assert got == 4
    assert notes == ["s4 counted by follow-through (no s2)"]


def test_score_rejects_unknown_and_broken():
    with pytest.raises(ValueError):
        score(GOOD, ["s9"])
    with pytest.raises(ValueError):
        score(bad(total=9), ["s1"])


def test_cli(capsys):
    assert main(["check", str(EX)]) == 0
    assert main(["score", str(EX), "s1", "s3", "s4", "s5"]) == 0
    out = capsys.readouterr().out
    assert "Marks: 4 out of 5" in out
    assert main(["check", "/nonexistent.json"]) == 1
    assert main([]) == 2
