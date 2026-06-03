#!/usr/bin/env python3
"""
Measure how much oracle text parses into Axis2 effects.

Usage:
  PYTHONPATH=src python3 scripts/parse_coverage.py
  PYTHONPATH=src python3 scripts/parse_coverage.py --limit 200 --json report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running without install
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from axis1.schema import Axis1Card
from axis2.compiler.card_compiler import CardCompiler
from scryfall.mappers.axis1_mapper import Axis1Mapper
from scryfall.client import ScryfallClient


def main():
    parser = argparse.ArgumentParser(description="Axis2 parse coverage report")
    parser.add_argument("--limit", type=int, default=100, help="Max cards to sample")
    parser.add_argument("--query", type=str, default="is:commander", help="Scryfall search query")
    parser.add_argument("--json", type=str, default="", help="Write JSON report to path")
    args = parser.parse_args()

    client = ScryfallClient()
    mapper = Axis1Mapper()
    compiler = CardCompiler()

    cards_raw = client.search(args.query)[: args.limit]

    total_clauses = 0
    parsed_clauses = 0
    fully_parsed_cards = 0
    samples_failed = []

    for raw in cards_raw:
        try:
            axis1 = mapper.map(raw)
        except Exception as e:
            samples_failed.append({"name": raw.get("name"), "error": str(e)})
            continue

        compiled = compiler.compile(axis1)
        r = compiled.report
        total_clauses += r.parsed_clause_count + len(r.unparsed_clauses)
        parsed_clauses += r.parsed_clause_count
        if r.fully_parsed:
            fully_parsed_cards += 1
        elif len(samples_failed) < 20:
            samples_failed.append(
                {
                    "name": r.card_name,
                    "unparsed": r.unparsed_clauses[:3],
                    "oracle_preview": r.oracle_text[:120],
                }
            )

    rate = (parsed_clauses / total_clauses * 100) if total_clauses else 0.0

    report = {
        "cards_tested": len(cards_raw),
        "clause_parse_rate_percent": round(rate, 2),
        "fully_parsed_cards": fully_parsed_cards,
        "sample_failures": samples_failed,
    }

    print(f"Cards tested: {report['cards_tested']}")
    print(f"Clause parse rate: {report['clause_parse_rate_percent']}%")
    print(f"Fully parsed cards: {report['fully_parsed_cards']}/{report['cards_tested']}")

    if samples_failed:
        print("\nSample unparsed (up to 20 cards):")
        for s in samples_failed[:10]:
            print(f"  - {s.get('name')}: {s.get('unparsed', s.get('error'))}")

    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2))
        print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
