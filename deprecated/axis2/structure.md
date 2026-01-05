# Axis2 Module Schema Documentation

## Overview

The `axis2` module is a **semantic parsing layer** that transforms raw card text (from Axis1) into structured, machine-readable representations (Axis2Card). It acts as a bridge between natural language card text and the game engine's rule system.

### Purpose

- Parse Oracle text into semantic effect objects
- Extract abilities, costs, targeting rules, and conditions
- Structure card data for consumption by Axis3 (the game engine)

---

## Architecture Overview

```
Axis1Card (raw text)
    ↓
Axis2Builder.build()
    ↓
Axis2Card (structured semantic data)
```

The transformation happens in multiple phases:

1. **Characteristics extraction** (mana cost, types, colors, etc.)
2. **Face parsing** (per face: abilities, effects, modes)
3. **Keyword expansion** (add implicit abilities)
4. **Assembly** into final Axis2Card

---

## File Structure & Responsibilities

### Core Files

#### `schema.py` (480 lines)

**Purpose**: Defines all data structures used in Axis2

**Key Classes**:

- `Axis2Card`, `Axis2Face`, `Axis2Characteristics` - Top-level card structures
- `Effect` hierarchy - Base class for all effects (DealDamageEffect, DrawCardsEffect, etc.)
- `Cost` types - ManaCost, TapCost, SacrificeCost, LoyaltyCost, EscapeCost
- `ActivatedAbility`, `TriggeredAbility` - Ability structures
- `StaticEffect`, `ReplacementEffect`, `ContinuousEffect` - Effect types
- `Subject` - Represents what an effect targets (creatures, players, etc.)
- `TargetingRules` - Rules for targeting in spells/abilities
- `ParseContext` - Context passed during parsing (card type, face info, etc.)

**Dependencies**: None (pure data structures)

---

#### `builder.py` (207 lines)

**Purpose**: Main orchestrator - builds Axis2Card from Axis1Card

**Key Flow**:

1. Extract characteristics from Axis1Face
2. For each face:

   - Parse special actions (Ninjutsu, repeatable payment)
   - Parse activated abilities
   - Parse triggered abilities (with delayed trigger synthesis)
   - Parse static effects
   - Parse modes
   - Parse spell effects (for instants/sorceries)
   - Parse replacement effects
   - Parse continuous effects

3. Extract keywords
4. Expand keywords (e.g., Treasure)
5. Assemble final Axis2Card

**Dependencies**:

- All parsing modules (activated, triggers, effects, targeting, etc.)
- `helpers.py` for text cleaning
- `expanding/keyword_expansion.py` for keyword expansion

---

#### `helpers.py` (36 lines)

**Purpose**: Utility functions for text manipulation

**Functions**:

- `cleaned_oracle_text()` - Removes activated/triggered ability text, leaving only static/continuous effects

**Dependencies**: `axis1.schema` (for Axis1Face)

---

### Parsing Modules (`parsing/`)

#### `effects.py` (1308 lines)

**Purpose**: Main effect parser - converts English text into Effect objects

**Key Functions**:

- `parse_effect_text()` - Main entry point, splits text and routes to specific parsers
- `split_effect_sentences()` - Splits multi-sentence effects
- Specific parsers: `parse_damage()`, `parse_draw()`, `parse_search()`, `parse_create_token()`, etc.

**Effect Types Handled**:

- Damage, Draw, Mana, Search, Create Token, Change Zone, Transform, Destroy, Counter Spell, etc.
- Conditional effects ("if you do", "if exiled this way")
- Look-and-pick effects
- Spell continuous effects (temporary P/T boosts)

**Dependencies**:

- `subject.py` - For parsing subjects
- `spell_continuous_effects.py` - For spell-based continuous effects
- `conditional_effects.py` - For conditional parsing
- `schema.py` - For Effect classes

---

#### `activated.py` (93 lines)

**Purpose**: Parses activated abilities (cost: effect format)

**Key Functions**:

- `parse_activated_abilities()` - Main entry point
- `split_full_ability()` - Splits "COST: EFFECT" format

**Flow**:

1. Extract cost and effect from Axis1Face
2. Parse costs using `costs.parse_cost_string()`
3. Parse effects using `effects.parse_effect_text()`
4. Parse targeting using `targeting.parse_targeting()`
5. Build ActivatedAbility object

**Dependencies**:

- `costs.py` - For cost parsing
- `effects.py` - For effect parsing
- `targeting.py` - For targeting rules

---

#### `triggers.py` (141 lines)

**Purpose**: Parses trigger event conditions

**Key Functions**:

- `parse_trigger_event()` - Converts trigger text to event objects
- `parse_spell_filter()` - Extracts spell type restrictions

**Event Types**:

- `ZoneChangeEvent` - "when X is put into graveyard"
- `EntersBattlefieldEvent` - "when X enters"
- `LeavesBattlefieldEvent` - "when X leaves"
- `DealsDamageEvent` - "when X deals damage"
- `CastSpellEvent` - "when you cast a spell"

**Dependencies**: `schema.py` (for event classes)

---

#### `targeting.py` (229 lines)

**Purpose**: Extracts targeting rules from effect text

**Key Functions**:

- `parse_targeting()` - Main entry point

**Handles**:

- Target types (creature, player, planeswalker, spell, etc.)
- Restrictions (nonland, you control, opponent controls, etc.)
- Multi-targeting ("up to N targets", "any number of targets")

**Dependencies**: `schema.py` (for TargetingRules)

---

#### `costs.py` (178 lines)

**Purpose**: Parses cost strings into Cost objects

**Key Functions**:

- `parse_cost_string()` - Main multi-part cost parser
- `parse_escape_cost()` - Special parser for Escape keyword

**Cost Types**:

- Mana costs (via `mana.parse_mana_cost()`)
- Tap costs (self or other permanents)
- Sacrifice costs
- Discard costs
- Loyalty costs

**Dependencies**:

- `mana.py` - For mana cost parsing
- `schema.py` - For Cost classes

---

#### `mana.py` (22 lines)

**Purpose**: Parses mana cost strings into ManaCost objects

**Key Functions**:

- `parse_mana_cost()` - Extracts mana symbols from strings like "{1}{R}{G}"

**Dependencies**: `schema.py` (for ManaCost)

---

#### `static_effects.py` (304 lines)

**Purpose**: Parses static abilities and effects

**Key Functions**:

- `parse_static_effects()` - Main entry point
- Specific parsers: `parse_blocking_restriction()`, `parse_cost_modification()`, etc.

**Handles**:

- Daybound/Nightbound
- Blocking restrictions
- Cost modifications
- Timing overrides (flash)
- Grant abilities (haste, etc.)

**Dependencies**:

- `helpers.py` - For text cleaning
- `schema.py` - For StaticEffect classes

---

#### `replacement_effects.py` (236 lines)

**Purpose**: Parses replacement effects ("if X would happen, Y instead")

**Key Functions**:

- `parse_replacement_effects()` - Main entry point

**Patterns Handled**:

- "If X would die, Y instead"
- "If X would be put into graveyard, Y instead"
- "Enter the battlefield tapped"
- Damage prevention/redirection
- Draw replacement
- Delayed replacement ("the next time X would happen")

**Dependencies**: `schema.py` (for ReplacementEffect, Subject)

---

#### `continuous_effects.py` (549 lines)

**Purpose**: Parses continuous effects (P/T modifications, ability grants, type changes, etc.)

**Key Functions**:

- `parse_continuous_effects()` - Main entry point
- `split_continuous_clauses()` - Splits multi-clause effects
- Specific parsers for P/T, abilities, colors, types

**Effect Kinds**:

- `pt_mod` - Power/toughness modifications
- `grant_ability` - Grant keywords
- `color_set`, `color_add` - Color changes
- `type_set`, `type_add`, `type_remove` - Type changes
- `ability_remove_all` - Remove all abilities
- Dynamic scaling (based on counters)

**Dependencies**:

- `subject.py` - For subject parsing
- `conditions.py` - For conditional parsing
- `schema.py` - For ContinuousEffect classes

---

#### `subject.py` (364 lines)

**Purpose**: Parses subject references ("target creature", "each creature you control", etc.)

**Key Functions**:

- `parse_subject()` - Main entry point
- `subject_from_text()` - Converts text to Subject object
- `_detect_scope()`, `_detect_controller()`, `_detect_types()` - Helper functions

**Subject Scopes**:

- `target` - Targeted objects
- `each` - All matching objects
- `self` - The card itself
- `that` - Referenced object
- `linked_exiled_card` - Special case for delayed triggers

**Dependencies**: `schema.py` (for Subject, ParseContext)

---

#### `modes.py` (23 lines)

**Purpose**: Parses modal spells ("Choose one —")

**Key Functions**:

- `parse_modes()` - Extracts modes from bulleted list format

**Dependencies**:

- `effects.py` - For parsing mode effects
- `targeting.py` - For parsing mode targeting

---

#### `trigger_filters.py` (43 lines)

**Purpose**: Parses trigger filters (who casts, spell types)

**Key Functions**:

- `parse_trigger_filter()` - Extracts controller scope and spell type restrictions

**Dependencies**: `schema.py` (for TriggerFilter)

---

#### `delayed_triggers.py` (44 lines)

**Purpose**: Synthesizes delayed triggers from "until X leaves" clauses

**Key Functions**:

- `has_until_leaves_clause()` - Detects the pattern
- `build_linked_return_trigger()` - Creates the return trigger

**Example**: "When X enters, exile Y until X leaves" → creates a second trigger that returns Y when X leaves

**Dependencies**:

- `triggers.py` - For LeavesBattlefieldEvent
- `schema.py` - For TriggeredAbility, ChangeZoneEffect

---

#### `conditional_effects.py` (75 lines)

**Purpose**: Parses conditional effects ("if you do", "if exiled this way", etc.)

**Key Functions**:

- `parse_conditional()` - Detects and extracts conditional clauses

**Condition Types**:

- `exiled_this_way` - "if a card is put into exile this way"
- `if_you_do` - "if you do"
- `kicked` - "if this spell was kicked"
- `cast_it` - "if you cast it"

**Dependencies**:

- `effects.py` - For parsing inner effects
- `schema.py` - For ConditionalEffect

---

#### `spell_continuous_effects.py` (44 lines)

**Purpose**: Parses temporary continuous effects from spells (e.g., "target creature gets +3/+3 until end of turn")

**Key Functions**:

- `parse_spell_continuous_effect()` - Detects P/T modifications with duration

**Dependencies**:

- `subject.py` - For subject parsing
- `continuous_effects.py` - For dynamic counter parsing
- `schema.py` - For ContinuousEffect

---

#### `conditions.py` (277 lines)

**Purpose**: Parses activation/trigger conditions (threshold, delirium, etc.)

**Key Functions**:

- `parse_condition()` - Main entry point
- Specific parsers: `parse_card_type_count_condition()`, `parse_threshold_condition()`, etc.

**Dependencies**: `schema.py` (for Condition class)

---

#### `sentences.py` (16 lines)

**Purpose**: Splits Oracle text into sentences

**Key Functions**:

- `split_into_sentences()` - Splits on periods, newlines, em-dashes

**Dependencies**: None

---

#### `keywords.py` (35 lines)

**Purpose**: Extracts standalone keyword lines (Flying, Vigilance, etc.)

**Key Functions**:

- `extract_keywords()` - Finds keywords that appear as standalone lines

**Dependencies**: None

---

### Expansion Modules (`expanding/`)

#### `keyword_expansion.py` (44 lines)

**Purpose**: Adds implicit abilities based on keywords/subtypes

**Key Functions**:

- `expand_treasure_keyword()` - Adds "{T}, Sacrifice: Add one mana of any color" to Treasure artifacts

**Dependencies**: `schema.py` (for ActivatedAbility, etc.)

---

### Parser Modules (`parsers/`)

#### `mana_cost_parser.py` (27 lines)

**Purpose**: Alternative mana cost parser (appears to be for Axis3 integration)

**Note**: This seems to be a different implementation than `parsing/mana.py` - may be legacy or for a different use case.

**Dependencies**: `axis3.rules.costs.mana` (different from axis2 schema)

---

## Data Flow

### Main Build Flow

```
Axis1Card
    ↓
Axis2Builder.build()
    ↓
    ├─→ Parse Characteristics (mana_cost, types, colors, etc.)
    │   └─→ mana.parse_mana_cost()
    │
    ├─→ For Each Face:
    │   │
    │   ├─→ Parse Special Actions
    │   │   ├─→ special_actions.parse_ninjutsu()
    │   │   └─→ special_actions.parse_repeatable_payment()
    │   │
    │   ├─→ Parse Activated Abilities
    │   │   └─→ activated.parse_activated_abilities()
    │   │       ├─→ costs.parse_cost_string()
    │   │       ├─→ effects.parse_effect_text()
    │   │       └─→ targeting.parse_targeting()
    │   │
    │   ├─→ Parse Triggered Abilities
    │   │   └─→ For each trigger:
    │   │       ├─→ triggers.parse_trigger_event()
    │   │       ├─→ effects.parse_effect_text()
    │   │       ├─→ targeting.parse_targeting()
    │   │       ├─→ trigger_filters.parse_trigger_filter()
    │   │       └─→ delayed_triggers.build_linked_return_trigger() (if needed)
    │   │
    │   ├─→ Parse Static Effects
    │   │   └─→ static_effects.parse_static_effects()
    │   │
    │   ├─→ Parse Modes
    │   │   └─→ modes.parse_modes()
    │   │
    │   ├─→ Parse Spell Effects (for instants/sorceries)
    │   │   └─→ effects.parse_effect_text() (with is_spell_text=True)
    │   │
    │   ├─→ Parse Replacement Effects
    │   │   └─→ replacement_effects.parse_replacement_effects()
    │   │
    │   └─→ Parse Continuous Effects
    │       └─→ continuous_effects.parse_continuous_effects()
    │
    ├─→ Extract Keywords
    │   └─→ keywords.extract_keywords()
    │
    ├─→ Expand Keywords
    │   └─→ keyword_expansion.expand_treasure_keyword()
    │
    └─→ Assemble Axis2Card
```

### Effect Parsing Flow

```
Text Input
    ↓
effects.parse_effect_text()
    ↓
    ├─→ Split into sentences
    │   └─→ split_effect_sentences()
    │
    ├─→ For each sentence:
    │   │
    │   ├─→ Check for conditional
    │   │   └─→ conditional_effects.parse_conditional()
    │   │
    │   ├─→ Try specific parsers (in order):
    │   │   ├─→ parse_look_and_pick()
    │   │   ├─→ parse_put_one_battlefield_tapped()
    │   │   ├─→ parse_search_effect()
    │   │   ├─→ parse_put_onto_battlefield()
    │   │   ├─→ parse_put_counter()
    │   │   ├─→ parse_create_token()
    │   │   ├─→ parse_damage()
    │   │   ├─→ parse_draw()
    │   │   ├─→ parse_add_mana_effect()
    │   │   ├─→ parse_change_zone()
    │   │   ├─→ parse_spell_continuous_effect()
    │   │   └─→ ... (many more)
    │   │
    │   └─→ Return list of Effect objects
    │
    └─→ Return combined effects
```

### Subject Parsing Flow

```
Text Input ("target creature you control")
    ↓
subject.parse_subject()
    ↓
    ├─→ Detect scope (target, each, self, that)
    │   └─→ _detect_scope()
    │
    ├─→ Detect controller (you, opponent, any)
    │   └─→ _detect_controller()
    │
    ├─→ Detect types (creature, artifact, etc.)
    │   └─→ _detect_types()
    │
    ├─→ Detect filters (keywords, power, etc.)
    │   └─→ _detect_filters()
    │
    └─→ Build Subject object
```

---

## Dependency Graph

### Core Dependencies

- `schema.py` ← All modules depend on this (data structures)
- `builder.py` ← Orchestrates all parsing modules
- `helpers.py` ← Used by builder and static_effects

### Parsing Module Dependencies

```
effects.py
    ├─→ subject.py
    ├─→ spell_continuous_effects.py
    ├─→ conditional_effects.py
    └─→ schema.py

activated.py
    ├─→ costs.py
    ├─→ effects.py
    ├─→ targeting.py
    └─→ schema.py

costs.py
    ├─→ mana.py
    └─→ schema.py

continuous_effects.py
    ├─→ subject.py
    ├─→ conditions.py
    └─→ schema.py

static_effects.py
    ├─→ helpers.py
    └─→ schema.py

delayed_triggers.py
    ├─→ triggers.py
    └─→ schema.py

spell_continuous_effects.py
    ├─→ subject.py
    ├─→ continuous_effects.py
    └─→ schema.py
```

### Independent Modules

- `sentences.py` - No dependencies
- `keywords.py` - No dependencies
- `mana.py` - Only depends on schema
- `triggers.py` - Only depends on schema
- `targeting.py` - Only depends on schema
- `trigger_filters.py` - Only depends on schema
- `modes.py` - Depends on effects and targeting

---

## Key Design Patterns

### 1. **Parser Pattern**

Each parsing module follows a similar pattern:

- Main entry function (e.g., `parse_effect_text()`)
- Specific pattern matchers (regex-based)
- Returns structured objects from schema

### 2. **Context Passing**

`ParseContext` is passed through parsing functions to provide:

- Card name, type, face info
- Whether parsing spell text vs static ability
- Whether parsing triggered ability

### 3. **Fallback Chain**

Effect parsing tries multiple parsers in sequence until one matches

### 4. **Subject Abstraction**

All targeting/subject references go through `Subject` objects, providing a unified interface

---

## Refactoring Considerations

### Current Issues

1. **Large effect parser** (`effects.py` - 1308 lines) - Could be split by effect type
2. **Tight coupling** - Many parsers directly import and call each other
3. **Regex-heavy** - Many pattern matchers could be abstracted
4. **Duplicate logic** - Some parsing logic duplicated across modules
5. **Mixed concerns** - Some modules handle both parsing and transformation

### Potential Improvements

1. **Split effects.py** into:

   - `effects/base.py` - Core parsing logic
   - `effects/damage.py` - Damage effects
   - `effects/search.py` - Search effects
   - `effects/tokens.py` - Token creation
   - etc.

2. **Create parser registry** - Central registry of effect parsers instead of hardcoded chain

3. **Abstract pattern matching** - Common regex patterns and matching logic

4. **Separate concerns** - Split parsing from transformation/validation

5. **Dependency injection** - Reduce direct imports, use dependency injection for testability

---

## Summary

The axis2 module is a **semantic parser** that transforms natural language card text into structured data. It uses a **modular parser architecture** where each module handles a specific aspect (effects, costs, targeting, etc.). The main orchestrator (`builder.py`) coordinates all parsers to build the final `Axis2Card` structure.

**Key Strengths**:

- Clear separation of concerns (mostly)
- Comprehensive coverage of MTG card text patterns
- Structured output ready for game engine consumption

**Key Weaknesses**:

- Large monolithic files (effects.py)
- Tight coupling between modules
- Regex-heavy, hard to maintain
- Some duplicate logic

This documentation should help identify refactoring opportunities and understand the current architecture before making changes.
