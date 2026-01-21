# Frontend Feature Modules

This directory contains feature modules organized by domain, following the Single Responsibility Principle (SRP).

## Architecture Overview

```
features/
├── game/                    # Game engine feature
│   ├── contexts/            # Split contexts for state management
│   │   ├── GameContext      # Core game state (gameId, gameState, cardMap)
│   │   ├── CombatContext    # Combat phase state (attackers, blockers, damage)
│   │   ├── CastingContext   # Spell casting (mana payment, costs)
│   │   ├── TargetingContext # Target selection and validation
│   │   └── ChoicesContext   # Modal, enter, search, replacement choices
│   ├── components/          # Feature components
│   │   └── ActionsPanel/    # Split actions panel
│   │       ├── CastingActions
│   │       ├── CombatActions
│   │       ├── TargetingSection
│   │       └── ChoicesSection
│   └── index.ts
└── builder/                 # Ability builder feature
    ├── components/
    │   └── EffectFields/    # Split effect fields
    │       ├── CommonFields
    │       ├── DamageEffectFields
    │       ├── DrawEffectFields
    │       ├── LifeEffectFields
    │       └── ManaEffectFields
    └── index.ts
```

## Dependency Rules

1. **Pages import from features** - Route pages use feature modules
2. **Features import from shared** - Features use hooks/, lib/, store/, context/, components/ui/
3. **Features do NOT import from other features** - Each feature is independent
4. **Shared modules do NOT import from features** - Shared code stays decoupled

## Game Feature

The game feature handles all gameplay functionality:

### Contexts

| Context | Responsibility |
|---------|---------------|
| GameContext | Core game state, session management, engine action execution |
| CombatContext | Attacker/blocker selection, damage assignments, combat validation |
| CastingContext | Spell preparation, mana payment, additional/alternative/optional costs |
| TargetingContext | Target selection, validation, copy spell targets |
| ChoicesContext | Modal choices, ETB choices, search choices, replacements |

### Components

| Component | Responsibility |
|-----------|---------------|
| ActionsPanel | Coordinator for game action UI |
| CastingActions | Cast spell, play land, tap for mana buttons |
| CombatActions | Declare attackers/blockers, combat damage |
| TargetingSection | Target selection UI |
| ChoicesSection | Modal, enter, search, replacement choice UI |

## Builder Feature

The builder feature handles ability graph construction:

### EffectFields Components

| Component | Effect Types |
|-----------|--------------|
| CommonFields | Shared fields (type, amount, target, duration) |
| DamageEffectFields | damage, damage_all, prevent_damage |
| DrawEffectFields | draw, mill, discard, loot |
| LifeEffectFields | gain_life, lose_life, set_life, pay_life |
| ManaEffectFields | add_mana, ritual |

## Usage Example

```typescript
// Importing from the game feature
import { 
  GameProvider, 
  useGame,
  ActionsPanel,
  CastingActions 
} from '@/features/game';

// Importing from the builder feature
import { 
  EffectFields,
  DamageEffectFields 
} from '@/features/builder';
```

## Migration Notes

This refactor was done to address SRP violations in:

1. **PlayState.tsx (1,332 lines)** → Split into 5 focused contexts (~150-250 lines each)
2. **ActionsPanel.tsx (950 lines, 100+ props)** → Split into coordinator + 4 sub-components
3. **EffectFields.tsx (1,139 lines)** → Split into coordinator + category components

The original files remain functional for backward compatibility, but new code should use the feature modules.
