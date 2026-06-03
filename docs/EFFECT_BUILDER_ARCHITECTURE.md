# Effect builder architecture

This repo had **three competing “builders”**. This document defines the **one correct pipeline** and what is deprecated.

> **Frontend UI wizard** (human effect picker with parameters): see [`FRONTEND_EFFECT_WIZARD.md`](./FRONTEND_EFFECT_WIZARD.md).  
> That lives under `frontend/` on the `frontend` branch / when merged. It is **not** the Axis2 oracle parser below.

## Canonical pipeline (use this)

```
Scryfall JSON
    → Axis1Mapper          (src/scryfall/mappers/axis1_mapper.py)
    → Axis2BuildPipeline   (src/axis2/build_pipeline.py)   ← “effect builder wizard”
    → Axis2Card            (typed Effect / Ability objects)
    → RuntimeObject        (src/axis3/integration/runtime_loader.py)
    → EffectExecutor       (src/axis3/runtime/effect_executor.py)
```

| Step | Module | Output |
|------|--------|--------|
| 1. Map card | `Axis1Mapper` | `Axis1Card` |
| 2. Build rules | `Axis2BuildPipeline` | `Axis2Card` |
| 3. Load into game | `create_runtime_object` | `RuntimeObject` + `axis2_card` |
| 4. Resolve | `EffectExecutor` | Game state changes |

## The Axis2 “wizard” (build pipeline)

`Axis2BuildPipeline` runs **ordered phases** on each face:

1. **Keywords** — strip keyword lines, emit keyword-derived effects  
2. **Ability boundaries** — split oracle into triggered / activated / spell / static / unknown chunks  
3. **Effect chains** — sentences + `parse_effect_text` (regex registry)  
4. **Emit** — `spell_effects`, `activated_abilities`, `triggered_abilities`, static/replacement/continuous  
5. **Merge Axis1** — structured abilities from Axis1 mapper when present  
6. **Post-process** — mana abilities, equip, modes, enchant restrictions  
7. **Keywords expand** — e.g. Treasure  
8. **Casting options** — flashback, escape, etc.  
9. **Validate** — `validate_axis2_card`

Parsing regex lives in `src/axis2/parsing/effects/`, not in the builder file.

## Deprecated / legacy (do not extend)

| Path | Problem |
|------|---------|
| `axis3/rules/builder/effects.py` | Re-parses oracle with **different** regex; calls `compile_effect` → `UnparsedEffect` |
| `axis3/compiler/axis3_builder.py` | Broken: undefined `triggered_abilities`, `compile_effects`, missing imports |
| `axis3/translate/compilers/effect_compiler.py` | Second regex path; use Axis2 `parse_effect_text` + `EffectExecutor` |
| `axis3/compiler/loader.py` (old) | Imported missing `axis3.cards.card_builder` |

## Adding new card text support

1. Add parser in `axis2/parsing/effects/` (or triggers/static/keywords)  
2. Register in `axis2/parsing/effects/__init__.py`  
3. Add handler in `axis3/runtime/effect_executor.py` if new `Effect` type  
4. **Do not** add regex to `axis3/rules/builder/`

## Debugging the wizard

```bash
PYTHONPATH=src python3 scripts/build_axis2_card.py --name "Lightning Bolt"
```

Prints build phases, effect counts per category, and structural/semantic coverage for one card.

## Coverage

```bash
PYTHONPATH=src python3 scripts/parse_coverage.py --limit 500
```

- **Structural** 100%: every clause → `Effect` (including `UnparsedOracleEffect`)  
- **Semantic**: % matched by specialized parsers (raise over time)
