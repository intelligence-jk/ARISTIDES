"""A scheme is JSON written by the teacher for their own question:

{"question": "Q1", "total": 5, "steps": [
   {"id": "s1", "type": "M", "marks": 1, "needs": [],     "note": "set up the equation"},
   {"id": "s2", "type": "A", "marks": 1, "needs": ["s1"], "note": "correct value"},
   {"id": "s3", "type": "B", "marks": 1, "needs": [],     "note": "independent fact"},
   {"id": "s4", "type": "M", "marks": 1, "needs": ["s2"], "ft": true, "note": "method on own value"},
   {"id": "s5", "type": "A", "marks": 1, "needs": ["s4"], "ft": true, "note": "answer from own value"}]}

Types: M method, A accuracy (only earned if the method it needs was earned), B independent.
"ft": true means follow-through is allowed (marks can be earned from the student's own earlier value).
"""
from fractions import Fraction as F

TYPES = ("M", "A", "B")


def _marks(v):
    f = F(str(v))
    return f


def check_scheme(scheme):
    """Return a list of problems with the scheme (empty means consistent)."""
    problems = []
    steps = scheme.get("steps") or []
    if not steps:
        return ["the scheme has no steps"]
    ids = []
    total = F(0)
    for i, s in enumerate(steps):
        sid = s.get("id")
        if not sid:
            problems.append(f"step {i + 1}: no id")
            continue
        if sid in ids:
            problems.append(f"{sid}: the id is used twice")
        if s.get("type") not in TYPES:
            problems.append(f"{sid}: type must be one of M, A, B")
        try:
            m = _marks(s.get("marks"))
        except (ValueError, TypeError, ZeroDivisionError):
            problems.append(f"{sid}: marks is not a number")
            m = F(0)
        else:
            if m <= 0:
                problems.append(f"{sid}: marks must be positive")
            if m.denominator != 1:
                problems.append(f"{sid}: marks must be a whole number")
        total += m
        needs = s.get("needs", [])
        for n in needs:
            if n == sid:
                problems.append(f"{sid}: a step cannot need itself")
            elif n not in ids:
                problems.append(f"{sid}: needs '{n}', which is not an earlier step")
        if s.get("type") == "A" and not needs:
            problems.append(f"{sid}: an A mark must need a method (M) step")
        if s.get("type") == "A" and needs:
            by = {x.get("id"): x for x in steps}
            if not any(by.get(n, {}).get("type") == "M" for n in needs if n in ids):
                problems.append(f"{sid}: an A mark must depend on at least one M step")
        if s.get("type") == "B" and needs:
            problems.append(f"{sid}: a B mark is independent, so it needs nothing")
        if s.get("ft") and s.get("type") == "B":
            problems.append(f"{sid}: follow-through does not apply to a B mark")
        ids.append(sid)
    declared = scheme.get("total")
    if declared is None:
        problems.append("the scheme gives no total")
    elif _marks(declared) != total:
        problems.append(f"the steps add to {_show(total)} but the total says {_show(_marks(declared))}")
    return problems


def _show(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def score(scheme, earned):
    """Total the marks for the step ids in `earned`, applying the dependency rules.

    An A step whose needed steps were not all earned is not counted unless it allows
    follow-through ("ft": true), in which case it is counted but flagged. Returns
    (marks, max_marks, notes).
    """
    problems = check_scheme(scheme)
    if problems:
        raise ValueError("the scheme is not consistent: " + "; ".join(problems))
    by = {s["id"]: s for s in scheme["steps"]}
    unknown = [e for e in earned if e not in by]
    if unknown:
        raise ValueError(f"not in the scheme: {', '.join(unknown)}")
    got, notes = F(0), []
    for s in scheme["steps"]:
        if s["id"] not in earned:
            continue
        missing = [n for n in s.get("needs", []) if n not in earned]
        if missing and not s.get("ft"):
            notes.append(f"{s['id']} not counted: needs {', '.join(missing)}")
            continue
        if missing:
            notes.append(f"{s['id']} counted by follow-through (no {', '.join(missing)})")
        got += _marks(s["marks"])
    return got, _marks(scheme["total"]), notes
