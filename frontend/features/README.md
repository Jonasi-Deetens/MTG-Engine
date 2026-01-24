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
│   ├── components/          # Game UI components
│   │   ├── ActionsPanel/    # Split actions panel (refactored)
│   │   ├── playmat/         # Play mat components
│   │   └── [panels]         # Individual game panels
│   ├── hooks/               # Game-specific hooks
│   └── index.ts
│
├── builder/                 # Ability builder feature
│   ├── components/
│   │   ├── EffectFields/    # Split effect fields (refactored)
│   │   ├── forms/           # Ability form components
│   │   └── [components]     # Builder UI components
│   └── index.ts
│
├── decks/                   # Deck management feature
│   ├── components/
│   │   ├── builder/         # Deck builder components
│   │   └── [components]     # Deck UI components
│   ├── hooks/               # Deck-specific hooks
│   └── index.ts
│
├── collections/             # Card collections feature
│   ├── components/          # Collection UI components
│   └── index.ts
│
├── search/                  # Card search feature
│   ├── components/          # Search UI components
│   ├── hooks/               # Search-specific hooks
│   └── index.ts
│
└── index.ts                 # Re-exports all features
```

## Dependency Rules

1. **Pages import from features** - Route pages use feature modules
2. **Features import from shared** - Features use lib/, store/, context/, components/ui/
3. **Features do NOT import from other features** - Each feature is independent
4. **Shared modules do NOT import from features** - Shared code stays decoupled

## Remaining Shared Code

The following stay in their original locations (not feature-specific):

- `components/ui/` - Generic UI primitives (Button, Card, Input, etc.)
- `components/navigation/` - App-wide navigation
- `components/skeletons/` - Loading skeletons
- `components/cards/` - Shared card display components
- `components/landing/` - Landing page components
- `components/dashboard/` - Dashboard widgets
- `hooks/useThemeImage.ts` - Generic theme utility
- `context/` - App-wide contexts (Auth, Theme, Shortcuts)

## Feature Details

### Game Feature

The game feature handles all gameplay functionality:

**Contexts:**
| Context | Responsibility |
|---------|---------------|
| GameContext | Core game state, session management, engine action execution |
| CombatContext | Attacker/blocker selection, damage assignments, combat validation |
| CastingContext | Spell preparation, mana payment, additional/alternative/optional costs |
| TargetingContext | Target selection, validation, copy spell targets |
| ChoicesContext | Modal choices, ETB choices, search choices, replacements |

**Components:**
| Component | Responsibility |
|-----------|---------------|
| ActionsPanel | Coordinator for game action UI (refactored version) |
| PlayerMat | Player's play area |
| StackView | Display of spell/ability stack |
| TurnStatusCard | Current turn/step display |
| ManaPaymentPanel, ActivationCostPanel, etc. | Cost payment UIs |

**Hooks:**
| Hook | Responsibility |
|------|---------------|
| useEffectGraphs | Load effect graphs for cards |
| useActivationCosts | Handle cost payments |
| useCasting | Spell casting flow |
| useCombatSelection | Attacker/blocker selection |
| useTargeting | Target selection and validation |
| useEffectTargeting | Effect-based targeting |
| useEngineActions | Engine API wrapper |
| useReplacementConflicts | Replacement effect conflicts |
| useWardPayments | Ward cost handling |

### Builder Feature

The builder feature handles ability graph construction:

**Components:**
| Component | Responsibility |
|-----------|---------------|
| EffectFields | Effect field coordinator (refactored) |
| LegacyEffectFields | Original monolithic effect fields (forms/EffectFields.tsx) |
| AbilityTabs | Ability type selector |
| AbilityTreeView | Graph visualization |
| ConditionBuilder | Condition configuration |
| CostListEditor | Cost entry management |
| ValidationPanel | Validation error display |
| *AbilityForm | Form for each ability type |

### Decks Feature

The decks feature handles deck building and management:

**Components:**
- DeckCard, DeckCardList, DeckValidationPanel
- ManaCurveChart, CardTypeBreakdown
- DeckImport, DeckImportExport
- EditableTypeList, UnifiedCardSearch
- Builder: DeckBuilderHeader, DeckInfoForm, CommanderSection, etc.

**Hooks:**
- useDeckBuilder, useDeckCardHandlers, useDragAndDrop, useTypeLists

### Collections Feature

Simple feature for card collections and favorites:
- AddToCollectionButton, FavoriteButton

### Search Feature

Card search functionality:
- SearchFilters, SearchHeader
- useCardSearch, useSearchFilters

## Usage Example

```typescript
// Importing from the game feature
import { 
  GameProvider, 
  useGame,
  ActionsPanel,
  useTargeting,
  useEngineActions
} from '@/features/game';

// Importing from the builder feature
import { 
  EffectFields,
  AbilityTabs,
  ValidationPanel
} from '@/features/builder';

// Importing from the decks feature
import {
  DeckCard,
  useDeckBuilder
} from '@/features/decks';
```

## Migration Notes

This refactor addressed SRP violations by:

1. Moving domain-specific components from `components/` to `features/`
2. Moving domain-specific hooks from `hooks/` to feature directories
3. Creating split contexts for PlayState functionality
4. Creating split ActionsPanel and EffectFields components

The original monolithic files remain as `Legacy*` versions for backward compatibility.
