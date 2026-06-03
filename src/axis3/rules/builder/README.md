# Deprecated: axis3/rules/builder

This package re-parses oracle text with **different regex** than Axis2.

Problems:
- Duplicates `axis2/parsing/effects/` registry
- Uses `compile_effect()` → legacy Axis3 regex, not `EffectExecutor`
- `derive_triggers()` conflicts with `axis2/builder.py` triggered parsing
- Debug `print()` statements left in `derive_effects()`

## Migration

| Old | New |
|-----|-----|
| `derive_triggers(axis1, gs)` | `Axis2BuildPipeline().build(axis1).faces[0].triggered_abilities` |
| `derive_effects(axis1, gs)` | `faces[0].spell_effects` |
| `compile_effect(line)` | `parse_effect_text(line, ctx)` then `EffectExecutor` |

See `docs/EFFECT_BUILDER_ARCHITECTURE.md`.
