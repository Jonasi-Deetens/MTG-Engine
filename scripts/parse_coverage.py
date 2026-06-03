#!/usr/bin/env python3
"""
Measure oracle text parsing coverage (structural + semantic).

Structural coverage: every clause maps to an Effect (100% with fallback parser).
Semantic coverage: specialized parsers matched (goal: raise over time).

Usage:
  PYTHONPATH=src python3 scripts/parse_coverage.py --limit 200
  PYTHONPATH=src python3 scripts/parse_coverage.py --bulk --limit 1000
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from axis2.compiler.card_compiler import CardCompiler
from scryfall.mappers.axis1_mapper import Axis1Mapper
from scryfall.client import ScryfallClient


def main():
    parser = argparse.ArgumentParser(description="Axis2 parse coverage report")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--query", type=str, default="is:commander")
    parser.add_argument("--bulk", action="store_true", help="Use bulk default-cards (slower)")
    parser.add_argument("--json", type=str, default="")
    args = parser.parse_args()

    mapper = Axis1Mapper()
    compiler = CardCompiler()
    cards_raw = []

    if args.bulk:
        import requests
        meta = requests.get(
            "https://api.scryfall.com/bulk-data/default-cards", timeout=30
        ).json()
        cards_raw = requests.get(meta["download_uri"], timeout=120).json()[: args.limit]
    else:
        client = ScryfallClient()
        cards_raw = client.search(args.query)[: args.limit]

    total_clauses = 0
    structural_parsed = 0
    semantic_parsed = 0
    fallback_clauses = 0
    fully_semantic_cards = 0
    errors = []
    samples_fallback = []

    for raw in cards_raw:
        try:
            axis1 = mapper.map(raw)
            compiled = compiler.compile(axis1)
        except Exception as e:
            errors.append({"name": raw.get("name"), "error": str(e)})
            continue

        r = compiled.report
        tc = r.parsed_clause_count + len(r.unparsed_clauses)
        total_clauses += tc
        structural_parsed += r.parsed_clause_count
        semantic_parsed += r.semantic_clause_count
        fallback_clauses += r.fallback_clause_count

        if tc > 0 and r.semantic_parse_rate >= 1.0:
            fully_semantic_cards += 1
        elif len(samples_fallback) < 15 and r.fallback_clause_count > 0:
            samples_fallback.append(
                {
                    "name": r.card_name,
                    "semantic_rate": round(r.semantic_parse_rate * 100, 1),
                    "fallback_clauses": r.fallback_clause_count,
                    "oracle_preview": r.oracle_text[:100],
                }
            )

    structural_rate = (structural_parsed / total_clauses * 100) if total_clauses else 100.0
    semantic_rate = (semantic_parsed / total_clauses * 100) if total_clauses else 100.0

    report = {
        "cards_tested": len(cards_raw) - len(errors),
        "errors": len(errors),
        "total_clauses": total_clauses,
        "structural_parse_rate_percent": round(structural_rate, 2),
        "semantic_parse_rate_percent": round(semantic_rate, 2),
        "fallback_clauses": fallback_clauses,
        "fully_semantic_cards": fully_semantic_cards,
        "sample_fallback_cards": samples_fallback,
    }

    print(f"Cards tested: {report['cards_tested']} ({report['errors']} errors)")
    print(f"Total oracle clauses: {total_clauses}")
    print(f"Structural parse rate: {report['structural_parse_rate_percent']}% (target: 100%)")
    print(f"Semantic parse rate:   {report['semantic_parse_rate_percent']}%")
    print(f"Fully semantic cards:  {fully_semantic_cards}/{report['cards_tested']}")

    if samples_fallback:
        print("\nSample cards using fallback parser:")
        for s in samples_fallback[:8]:
            print(f"  - {s['name']} ({s['semantic_rate']}% semantic)")

    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2))
        print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
