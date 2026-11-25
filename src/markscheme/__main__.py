"""python -m markscheme check SCHEME.json | score SCHEME.json s1 s2 ..."""
import json
import sys

from .core import _show, check_scheme, score


def main(argv=None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if a[:1] in (["check"], ["score"]) and len(a) >= 2:
        try:
            scheme = json.load(open(a[1]))
            if a[0] == "check":
                problems = check_scheme(scheme)
                print("\n".join(problems) if problems else "OK")
                return 1 if problems else 0
            got, mx, notes = score(scheme, a[2:])
        except (OSError, ValueError) as e:
            print(f"Cannot do that: {e}", file=sys.stderr)
            return 1
        print("\n".join(notes))
        print(f"Marks: {_show(got)} out of {_show(mx)}")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
