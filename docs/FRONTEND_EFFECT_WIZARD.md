# Frontend effect wizard (Ability Builder)

The interactive UI for defining card effects lives on the **`frontend`** branch under:

| Path | Role |
|------|------|
| `frontend/app/(protected)/builder/page.tsx` | Ability Builder page (`/builder`) |
| `frontend/features/builder/components/EffectWizard/` | Multi-step modal wizard |
| `frontend/store/effectStore.ts` | Zustand store → `EffectGraph` |
| `frontend/lib/unifiedEffect.ts` | Typed effect model |
| `frontend/lib/effectTypes.ts` | Effect type options + `getEffectTypeOption()` |
| `frontend/lib/effectValidation.ts` | Client-side zod validation |
| `frontend/lib/effectWizardSteps.ts` | Wizard step flow (which steps to show) |

## Wizard flow

1. **Intent** — triggered, activated, always-on, spell, replacement, prevention, keyword  
2. **Setup** — trigger / activation cost / continuous / replacement config (skipped for simple spells)  
3. **Conditions** — optional gates  
4. **Extra costs** — kicker / additional / optional costs (spell graphs only)  
5. **Effect** — one-shot action parameters (amount, target, search, tokens, …)  
6. **Review** — confirm and save into the effect list  

Activation costs are edited in **Setup** (via `CostListEditor`). Spell-only extra costs are in **Extra costs**.

## Backend

- Graphs are stored per card via `POST/GET /api/effects/cards/{card_id}/effects`  
- Validation: `POST /api/effects/validate` (Pydantic, mirrors frontend zod)  
- Oracle parsing pipeline (`Axis2BuildPipeline`) is separate — used to *import* text, not to drive this UI  

## Not the same as Axis2 build pipeline

| | Frontend wizard | Axis2 pipeline |
|--|-----------------|----------------|
| User | Human picks effect + parameters | Automated regex on oracle text |
| Output | `EffectGraph` JSON | `Axis2Card` dataclasses |
| Location | `frontend/` | `src/axis2/` |
