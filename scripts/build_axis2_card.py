#!/usr/bin/env python3
"""
Run the Axis2 effect-builder wizard on one card and print a build report.

Examples:
  PYTHONPATH=src python3 scripts/build_axis2_card.py --name "Lightning Bolt"
  PYTHONPATH=src python3 scripts/build_axis2_card.py --json path/to/card.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from axis2.build_pipeline import Axis2BuildPipeline, BuildPhase, PHASE_DESCRIPTIONS
from axis2.compiler.card_compiler import CardCompiler
from scryfall.mappers.axis1_mapper import Axis1Mapper


def _print_phases(report) -> None:
    print("Build phases:")
    seen = set()
    for name in report.phases_run:
        if name in seen:
            continue
        seen.add(name)
        try:
            phase = BuildPhase[name]
            desc = PHASE_DESCRIPTIONS.get(phase, "")
        except KeyError:
            desc = ""
        print(f"  - {name}" + (f": {desc}" if desc else ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Axis2 effect builder wizard")
    parser.add_argument("--name", help="Card name to fetch from Scryfall")
    parser.add_argument("--json", type=Path, help="Local Scryfall JSON file")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not args.name and not args.json:
        parser.error("Provide --name or --json")

    if args.json:
        data = json.loads(args.json.read_text())
    else:
        from scryfall.client import ScryfallClient

        data = ScryfallClient().get_card_by_name(args.name)

    axis1 = Axis1Mapper().map(data)
    pipeline = Axis2BuildPipeline(verbose=args.verbose)
    axis2, report = pipeline.build_with_report(axis1)
    compiled = CardCompiler(builder=pipeline).compile(axis1)

    name = axis1.names[0] if axis1.names else "?"
    print(f"Card: {name}")
    _print_phases(report)

    face = axis2.faces[0]
    print(f"\nSpell effects: {len(face.spell_effects)}")
    print(f"Triggered: {len(face.triggered_abilities)}")
    print(f"Activated: {len(face.activated_abilities)}")
    print(f"Static: {len(face.static_abilities)}")
    print(f"Replacement: {len(face.replacement_effects)}")
    print(f"Continuous: {len(face.continuous_effects)}")

    r = compiled.report
    print(
        f"\nCoverage: structural={r.structural_parse_rate:.1%} "
        f"semantic={r.semantic_parse_rate:.1%} "
        f"fallback_clauses={r.fallback_clause_count}"
    )
    if report.warnings:
        print("\nWarnings:")
        for w in report.warnings:
            print(f"  - {w}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
