#!/usr/bin/env python3
"""Compare the objdiff report with a saved baseline and list what changed.

Used as the no-regression gate before a commit.

Usage:
  python tools/report_diff.py --save            # save build/NPUG80330/report.json as the baseline
  python tools/report_diff.py                   # compare the current report with the baseline
  python tools/report_diff.py --base other.json # compare with another report
  python tools/report_diff.py --version NPUG80330

Exit status 1 when a function present in both reports lost match percentage, or a
fully matched function or data section disappeared without a 100 % replacement.
"""

import argparse
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VERSION = "NPUG80330"


def load(path):
    """(measures, {key: percent}, {key: unit name})."""
    with open(path, encoding="utf-8") as f:
        report = json.load(f)
    items, units = {}, {}
    for unit in report["units"]:
        name = unit["name"]
        # Functions are keyed by symbol name only (unique in the module), so a
        # function that moves from an assembly piece (asm/<module>/text_<vram>,
        # renamed whenever a unit is split out) to a source file is compared, not
        # removed and re-added.
        for func in unit.get("functions", []):
            key = ("fn", func["name"])
            items[key] = func.get("fuzzy_match_percent", 0.0)
            units[key] = name
        # Data sections of assembly pieces are not diffed, and their names repeat.
        if name.startswith("asm/"):
            continue
        for section in unit.get("sections", []):
            if section["name"].startswith(".text"):
                continue
            key = ("data", f"{name} {section['name']}")
            items[key] = section.get("fuzzy_match_percent", 0.0)
            units[key] = name
    return report["measures"], items, units


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", default=DEFAULT_VERSION,
                        help="game version (default: %(default)s)")
    parser.add_argument("--save", action="store_true", help="save the current report as the baseline")
    parser.add_argument("--base", help="baseline report (default: build/<version>/report_base.json)")
    args = parser.parse_args()
    report = os.path.join(ROOT, "build", args.version, "report.json")
    if args.base is None:
        args.base = os.path.join(ROOT, "build", args.version, "report_base.json")

    if args.save:
        shutil.copyfile(report, args.base)
        print(f"Saved baseline to {args.base}")
        return 0
    if not os.path.exists(args.base):
        print(f"No baseline at {args.base}; run with --save first", file=sys.stderr)
        return 2

    base_measures, base, base_units = load(args.base)
    cur_measures, cur, cur_units = load(report)

    regressions, improvements, removed, added = [], [], [], []
    for key in sorted(set(base) | set(cur)):
        old, new = base.get(key), cur.get(key)
        if old is None:
            added.append((key, new))
        elif new is None:
            removed.append((key, old))
        elif new < old:
            regressions.append((key, old, new))
        elif new > old:
            improvements.append((key, old, new))

    # A matched item that only changed name (symbol renamed) is not a regression.
    added_full = sum(1 for _, pct in added if pct == 100.0)
    removed_full = [(key, pct) for key, pct in removed if pct == 100.0]
    lost = removed_full[added_full:] if len(removed_full) > added_full else []

    def fmt(key):
        kind, name = key
        if kind == "data":
            return f"data {name}"
        old, new = base_units.get(key), cur_units.get(key)
        where = old or new if old == new or None in (old, new) else f"{old} -> {new}"
        return f"{where} fn {name}"

    for title, rows in (("Regressions", regressions), ("Improvements", improvements)):
        if rows:
            print(f"{title}:")
            for key, old, new in rows:
                print(f"  {fmt(key)}: {old:.2f} -> {new:.2f}")
    if removed or added:
        print(f"Removed: {len(removed)} ({len(removed_full)} at 100 %), "
              f"added: {len(added)} ({added_full} at 100 %)")
        for key, pct in removed:
            print(f"  - {fmt(key)} ({pct:.2f})")
        for key, pct in added:
            print(f"  + {fmt(key)} ({pct:.2f})")

    for field in ("matched_code", "complete_code", "matched_data", "matched_functions"):
        old, new = int(base_measures.get(field, 0)), int(cur_measures.get(field, 0))
        if old != new:
            print(f"{field}: {old} -> {new} ({new - old:+d})")

    if regressions or lost:
        print("FAIL: regressions found")
        return 1
    print("OK: no regression")
    return 0


if __name__ == "__main__":
    sys.exit(main())
