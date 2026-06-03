# Rules core (Regels)

You **need** this layer. Card parsing alone is not enough to play Magic.

## Two different problems

| Layer | Question it answers | Example |
|-------|---------------------|---------|
| **Axis1 / Axis2** | What does this card *say*? | "Deal 3 damage to any target" → `DealDamageEffect` |
| **Rules core (here)** | What does the *game* allow? | Only one land per turn; sorceries in main phase with empty stack |

Comprehensive Rules (CR) define the game. Oracle text defines cards. A simulator needs **both**.

## What lives here

- `catalog.py` — maps CR sections to engine modules (documentation + coverage tracking)
- `permissions.py` — timing, priority, lands, zones (simple rules)
- `engine.py` — `GameRulesEngine` facade used by actions and casting

## What lives elsewhere (still “rules”, different subsystems)

- `rules/sba/` — state-based actions (CR 704)
- `rules/atomic/` — draw, damage, zone change events
- `rules/replacement/` — replacement effects (CR 616)
- `rules/layers/` — continuous effects (CR 613)
- `engine/turn/` — turn structure (CR 500–514)
- `runtime/effect_executor.py` — executes parsed card effects

## Mental model

```
Player action → GameRulesEngine (legal?) → stack/costs → EffectExecutor (resolve card text) → SBAs
```

Without the middle “legal?” step, you can parse Lightning Bolt perfectly and still allow casting it during the opponent’s untap step with three sorceries on the stack.
