# marking-scheme-checker

Check a marking scheme you wrote for your own question, then total a student's awarded marks against it with the dependency rules applied.

## What it solves
A home-made marking scheme often has quiet errors: the steps add to 6 but the question says 5, an accuracy mark that does not depend on any method mark, a step that needs a step written later. Those errors turn into unfair marking. This tool reads a small JSON scheme, lists every inconsistency, and then totals the marks a student earned, refusing to count an accuracy mark whose method mark was not earned (unless you marked it follow-through). It contains no exam-board scheme or question text: you write the scheme for your own questions. Pure Python 3.10+, standard library only, exact `Fraction` arithmetic.

## Example
`examples/q1.json` is a scheme for "Solve 3x + 2 = 20 and then find 2x + 1" (five marks: M, A, B, then M and A on follow-through).
```bash
python -m markscheme check examples/q1.json
python -m markscheme score examples/q1.json s1 s3 s4 s5
python -m markscheme score examples/q1.json s2 s3
```
Output of a real run:
```
OK
s4 counted by follow-through (no s2)
Marks: 4 out of 5
s2 not counted: needs s1
Marks: 1 out of 5
```
The second run is a student who set up the equation, wrote 2x + 1, and used a wrong x (so no s2): they keep the later method and answer marks by follow-through. The third run is a student who wrote x = 6 with no working shown: the accuracy mark s2 needs the method mark s1, so only the independent B mark counts.

## The maths behind it
The scheme is a small graph: each step has a type (M method, A accuracy, B independent), a whole number of marks and the earlier steps it needs. The checks are exact: the marks add to the stated total (here 1 + 1 + 1 + 1 + 1 = 5), every step needs only earlier steps (so there is no loop), every A needs at least one M, a B needs nothing. Scoring walks the steps in order; a step is counted when everything it needs was earned, or when it allows follow-through, in which case it is counted and flagged so the marker can see it. For the example question, 3x + 2 = 20 gives 3x = 18, x = 6, and 2x + 1 = 13.

## Install and run
```bash
python -m pip install -e .
python -m markscheme check examples/q1.json
python -m pytest
```

## Licence
MIT. Made by Math & Myth (mathandmyth.ae): one to one maths mentoring, online, across the UAE.
