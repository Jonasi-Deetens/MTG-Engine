# Card text parsing (regex + structure)

To turn **all cards** into **executable effects**, you need a text compiler. Regex is a core tool — but not as one 10,000-line file.

## Pipeline

```
Scryfall JSON
    → Axis1 (layout, types, raw oracle)
    → Axis2 builder
         ├─ ability_boundaries (split into triggered / activated / spell / …)
         ├─ keyword_abilities/ (150+ keyword parsers)
         ├─ effects/ registry (regex per effect type)
         ├─ triggers/, static_effects/, replacement_effects/, …
    → Axis2Card (typed Effect objects)
    → axis3.runtime.EffectExecutor (runs effects in game)
```

## Where regex lives

| Module | Role |
|--------|------|
| `effects/damage.py` | `deals N damage to …` |
| `effects/draw.py` | `draw a card` |
| `effects/search.py` | `search your library for …` |
| `effects/registry.py` | Tries parsers in priority order |
| `ability_boundaries.py` | Splits oracle on When / colon costs / static starters |
| `activated.py` | `{T}: effect` lines |

Each parser uses **small, testable regexes** + `Subject` extraction. Adding a card pattern = add or extend one parser file, register it in `effects/__init__.py`.

## What regex cannot do alone

- **100% oracle coverage** without ongoing parser work (new mechanics, weird wording)
- **Targeting choices** (needs game UI / AI)
- **Rules legality** (priority, timing) — that's `axis3/rules/`, not parsing

## Coverage workflow

```bash
PYTHONPATH=src python3 scripts/parse_coverage.py --limit 500
```

Use `axis2.compiler.CardCompiler` for per-card `ParseReport` (parsed vs unparsed clauses).

## Goal

**Executable** means: every parsed clause becomes an `axis2.schema.Effect` subclass that `EffectExecutor` knows how to run. Unparsed clauses stay in `ParseReport.unparsed_clauses` until a new parser is added.
