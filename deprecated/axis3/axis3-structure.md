axis3/

- abilities/
    -- activated.py:

    RuntimeActivatedAbility

Purpose: Represents an activated ability of a card in the runtime game state.

Responsibilities:

Stores the ability’s source, controller, cost, and effect.

Tracks activation restrictions (e.g., once per turn, tapped requirements).

Handles activation logic: either resolves immediately (mana abilities) or pushes to the game stack for later resolution.

Key Methods:

can_activate(game_state): Checks if the ability can be legally activated.

activate(game_state): Activates the ability; either resolves immediately or pushes a StackItem to the stack.

Notes: This class is central to executing card abilities in-game and interacts closely with the stack system for non-mana abilities.

    -- keyword.py:

    Keyword Ability Handling

Purpose: Manages standard keyword abilities (e.g., flying, haste) for runtime objects.

Responsibilities:

Collects keywords from printed characteristics and continuous effects.

Filters out invalid or unsupported keywords.

Updates the EvaluatedCharacteristics for the object (typically in Layer 6).

Key Function:

apply_keyword_abilities(game_state, rt_obj, ec): Computes the final set of keywords for an object at the relevant layer.

Notes: Central to Layer-based evaluation of abilities; ensures objects have correct keywords after continuous effects are applied.

    -- static.py:

    Defines runtime representations of static and continuous effects:

RuntimeContinuousEffect: Represents a continuous effect from a permanent or spell, including power/toughness modifications, added/removed abilities, types, subtypes, supertypes, colors, and keywords. Each effect includes a layer (and optional sublayer) and an applies_to function to determine which objects it affects.

RuntimeStaticAbility: A container for one or more continuous effects attached to a permanent. Its apply method executes all relevant effects on an object's evaluated characteristics, respecting layer and sublayer ordering.

Essentially, this module handles all continuous, ongoing modifications and static abilities that affect permanents during gameplay evaluation.

    -- triggered.py:

    Defines runtime triggered abilities:

RuntimeTriggeredAbility: Represents a triggered ability in the game runtime.

source_id: The object that owns the ability.

controller: The player who controls the ability.

axis2_trigger: Reference to the original Axis2-level trigger object, containing its effect text, conditions, etc.

These abilities are typically pushed onto the stack when their triggering condition occurs and then resolved according to the game’s stack rules. Essentially, this module is for all triggered abilities that can respond to game events.

- rules/
    -- atomic/
        --- damage.py:

        Handles applying damage to objects and players.

Purpose: Implements the atomic rule for dealing damage. This is the low-level logic that directly modifies life totals or creature damage counters when a damage event occurs.

Key Details:

Function: apply_damage(game_state, event: Event)

Input: event.payload must include:

target_id → player or permanent receiving damage

amount → damage quantity

damage_type → optional, defaults to "default"

Steps:

Apply replacement effects via apply_replacements before any damage is dealt.

Check target type:

If target_id corresponds to a player, subtract from their life and publish a LIFE_CHANGE event.

If target_id corresponds to a permanent on the battlefield, increment its .damage field and publish a DAMAGE event.

Skip invalid or off-zone targets.

Usage:

Called when any effect deals damage, whether from spells, abilities, or combat.

Integrates with replacement effects and event publishing, ensuring triggers or further effects can respond to damage.

In short: this file provides the core rule logic for handling damage, applying it safely to objects or players and firing the appropriate events.

        --- dispatch.py:

        Routes events to the correct atomic game rules.

Purpose: Acts as the central dispatcher for atomic events. Each EventType that directly modifies game state (like life, damage, draw, zone changes) is routed to its corresponding low-level rule function.

Key Details:

Function: apply_atomic_event(game_state, event: Event)

Input: event → an instance of Event with a type and payload.

Routing logic:

EventType.DRAW → calls draw.apply_draw(...)

EventType.DAMAGE → calls damage.apply_damage(...)

EventType.LIFE_CHANGE → calls life.apply_life_change(...)

EventType.ZONE_CHANGE → calls zone_change.apply_zone_change(...)

Events like CAST, TRIGGERED, or ABILITY_ADDED do not directly mutate state and are ignored here.

Usage:

Always called by the Game Orchestrator when an event reaches the atomic layer.

Ensures a single, consistent entry point from high-level events to low-level state changes.

In short: this file is the router from EventType → concrete game-rule logic, isolating event handling from the core rule implementations.

        --- draw.py:

        Handles drawing cards for a player.

Purpose: Moves cards from a player’s library to their hand while respecting replacement effects.

Key Function: apply_draw(game_state, event: Event)

Input: event with payload containing:

player_id → the player drawing the cards

amount → number of cards to draw (default 1)

Process:

Applies any relevant replacement effects to the draw event.

Iterates amount times:

Pops the top card from the player’s library.

Appends it to the player’s hand.

Updates the card’s zone to HAND.

Publishes a DRAW event for the specific card.

Usage: Called by the atomic event dispatcher whenever a draw event occurs. Ensures that library order, hand state, and event notifications are handled consistently.

In short: this file is the low-level rule logic for drawing cards, integrating with the replacement system and event bus.
        
        --- life.py:

        Handles changes to a player's life total.

Purpose: Adjusts a player’s life total, either increasing (gain) or decreasing (loss), while respecting replacement effects.

Key Function: apply_life_change(game_state, event: Event)

Input: event with payload containing:

player_id → the player whose life changes

amount → integer representing life change (positive or negative)

Process:

Applies replacement effects to the life change event.

Updates the player’s life total by amount.

Publishes a LIFE_CHANGE event on the event bus to notify other systems.

Usage: Called by the atomic event dispatcher for life gain/loss events, ensuring that all game effects that depend on life changes are properly triggered.

In short: this file is the core logic for directly modifying a player’s life total within Axis3’s atomic rules system.

        --- zone_change.py:

        Handles moving objects between zones.

Purpose: Implements the atomic rules for zone changes, e.g., casting a spell, putting a permanent on the battlefield, or moving cards to the graveyard. It ensures replacement effects are applied and generates derived events like ENTERS_BATTLEFIELD, LEAVES_BATTLEFIELD, or dies.

Key Function: apply_zone_change(game_state, event: Event)

Input: event.payload must include:

obj_id → the object being moved

from_zone → current zone

to_zone → destination zone

controller → controlling player

cause → optional reason for the move

Process:

Applies replacement effects first (apply_replacements).

Moves the object from the old zone to the new zone in game_state.

Resets damage if leaving the battlefield.

Publishes derived events based on the move:

LEAVES_BATTLEFIELD if leaving battlefield

ENTERS_BATTLEFIELD if entering battlefield

dies if a creature goes from battlefield → graveyard

Usage: Called whenever an object changes zones to correctly update game state and trigger related rules, events, and SBAs.

In short: this is the core logic for handling card/creature movements and generating related events in Axis3.

    -- costs/
        --- alternative.py:

        Handles alternative costs for spells and abilities.

Purpose: Represents costs that can be paid instead of a spell’s normal mana cost, such as paying life, discarding a card, or sacrificing a permanent.

Key Class: AlternativeCost

Attributes:

description → human-readable text describing the alternative cost.

pay_func → function implementing the cost logic.

Methods:

can_pay(game_state, player_id) → checks if the player is able to pay the alternative cost without executing it.

pay(game_state, player_id) → executes the cost, modifying the game state.

Example Function: discard_card_cost(game_state, player_id, check_only=False)

Checks if a card can be discarded (check_only=True) or actually discards the top card from the player’s hand and moves it to the graveyard.

Usage: You can create an instance of AlternativeCost for any spell, e.g., discard_cost, and integrate it with the spell’s payment logic.

In short: this file is for defining and executing alternative payment options for spells/abilities, keeping checks and execution separate.

        --- mana.py:

        Handles generic and colored mana costs for spells and abilities.

Purpose: Represents a spell’s mana cost and provides methods to check and pay it from a player’s mana pool.

Key Class: ManaCost

Attributes:

colorless → amount of generic (colorless) mana required.

colored → dictionary of colored mana required, e.g., {'G':2, 'U':1}.

Methods:

total() → returns total mana required (colored + colorless).

can_pay(player) → checks if a player’s mana pool has enough mana to pay the cost.

pay(player) → deducts mana from the player’s mana pool; colored mana is spent first, then generic mana from any color.

Usage: This class is used whenever a spell or ability requires mana to cast or activate, providing both validation and execution of payment.

In short: this file encapsulates all logic for checking and paying mana costs for the game engine.

        --- reduction.py:

        Handles cost reduction effects for spells and abilities.

Purpose: Provides a mechanism to reduce a spell’s generic mana cost based on static or conditional effects.

Key Class: CostReduction

Attributes:

description → textual explanation of the reduction (for logging or UI).

amount → how much generic mana is reduced.

condition → optional function (game_state, player_id, spell) -> bool that determines if the reduction applies.

Method:

apply(game_state, player_id, spell_cost) → reduces spell_cost.colorless by amount if condition is met. Ensures cost never drops below 0.

Usage: Used when effects like “Spells you cast cost {1} less” or other conditional reductions are in play. Integrates with ManaCost objects to dynamically adjust costs.

In short: this file encapsulates logic for applying generic mana reductions to spells, respecting conditions and the game state.

    -- events/
        --- bus.py:

        Central event management system for the game engine.

Purpose: Manages all game events, ensuring proper sequencing, replacement effects, triggers, and state-based actions (SBAs). Acts as the core of the event-driven architecture in Axis3.

Key Class: EventBus

Attributes:

game_state → the current GameState object.

queue → an EventQueue storing events to be processed in order.

triggers → a TriggerRegistry that tracks event-based triggers.

Methods:

publish(event) → public entry point for events; pushes them to the queue and processes them.

_drain() → processes events from the queue, in order:

Apply replacement effects (apply_replacements).

Apply atomic game rules (apply_atomic_event).

Notify triggers (self.triggers.notify).

Run state-based actions (run_sbas).

subscribe(event_type, callback) → allows external code to register callbacks for specific event types.

Usage: All changes in the game (drawing cards, damage, life gain/loss, zone changes, etc.) are routed through the EventBus to ensure consistent, rule-compliant processing.

In short: this file implements the event-driven backbone of the Axis3 engine, ensuring correct handling of effects, triggers, and game rules in the proper order.

        --- event.py:

        Immutable container for game events.

Purpose: Represents a single, discrete game event in Axis3. Events are the building blocks for the event-driven engine.

Key Class: Event

Attributes:

type → a string identifying the kind of event (e.g., "DRAW", "DAMAGE", "ZONE_CHANGE").

payload → a dictionary containing all data relevant to the event (e.g., player IDs, object IDs, amounts).

Behavior:

Immutable (frozen=True), ensuring events cannot be accidentally modified once created.

Serializable and replayable, making it suitable for logging, testing, and undo/redo mechanics.

Custom __repr__ for readable debugging output.

Usage: Events are created whenever something happens in the game (damage, life change, drawing cards, moving objects, etc.) and are passed through the EventBus to trigger replacements, SBAs, and triggers.

In short: this file defines the standardized, immutable structure for all game events in Axis3.

        --- queue.py:

        Simple FIFO queue for game events.

Purpose: Provides a first-in-first-out (FIFO) container to manage Event objects before they are processed by the EventBus.

Key Class: EventQueue

Internal Structure: Uses collections.deque for efficient append/pop operations.

Methods:

push(event) → Adds an Event to the end of the queue.

pop() → Removes and returns the first Event in the queue.

is_empty() → Checks if the queue is empty.

clear() → Empties the queue completely.

Usage: The EventBus uses this queue to sequentially process events, ensuring that events are handled in the order they were generated.

In short: this file defines a lightweight, ordered container for temporarily storing events before they are dispatched.

        --- types.py:

        Central registry of all game event type constants.

Purpose: Defines string constants representing every type of event that can occur in the Axis3 game engine. These constants are used in Event objects to categorize actions, allowing the EventBus and other systems to process them correctly.

Key Points:

Zones & Movement: e.g., ZONE_CHANGE, ENTERS_BATTLEFIELD, LEAVES_BATTLEFIELD

Card Flow: e.g., DRAW, DISCARD, MILL, SEARCH_LIBRARY

Life & Damage: e.g., DAMAGE, LIFE_CHANGE, PREVENT_DAMAGE

Counters & Characteristics: e.g., ADD_COUNTER, REMOVE_COUNTER, MODIFY_POWER_TOUGHNESS

Tap/Status: e.g., TAP, UNTAP, BECOMES_TAPPED

Stack & Spells: e.g., CAST_SPELL, PUT_ON_STACK, RESOLVE_STACK_OBJECT

Abilities: e.g., TRIGGERED_ABILITY, ACTIVATED_ABILITY, STATIC_ABILITY_APPLIED

Combat: e.g., DECLARE_ATTACKERS, DECLARE_BLOCKERS, COMBAT_DAMAGE, CREATURE_DIES

Turn Structure: e.g., BEGIN_STEP, END_STEP, BEGIN_PHASE, END_PHASE

Usage:

When creating an event:

from axis3.rules.events.types import EventType
Event(type=EventType.DRAW, payload={"player_id": 0, "amount": 1})


Systems (stack resolver, triggers, replacement effects, SBAs) match events against these constants to determine behavior.

In short: this file is the authoritative list of all event types in the game, ensuring consistent handling across the engine.

    -- layers/
        --- layersystem.py:

        Core evaluation engine for continuous effects and static abilities (MTG layers 1–7).

Purpose:
This system calculates the current characteristics of any permanent in the game, taking into account:

Base printed values (RuntimeCharacteristics)

Continuous effects from any source (RuntimeContinuousEffect)

Static abilities attached to the object (RuntimeStaticAbility)

Layered rules of Magic (1–7) including type, color, power/toughness, and abilities

Key Components:

evaluate(obj_id):

Returns EvaluatedCharacteristics for a permanent.

Steps:

Start from base printed characteristics.

Apply continuous effects (_apply_continuous_effects).

Apply layers 1–3 (supertype, type, subtype).

Apply static abilities in layers 4–7, sorted by sublayer.

Layer 6 additionally applies keyword abilities (apply_keyword_abilities).

_apply_continuous_effects(rt_obj, ec):

Iterates over game_state.continuous_effects.

Checks applies_to for each effect.

Applies P/T changes, type/color/ability modifications.

Layers 1–3 placeholders:

_apply_layer1: supertype modifications

_apply_layer2: type modifications

_apply_layer3: subtype modifications

Can be expanded to implement detailed layer-specific rules

Static Abilities Handling:

Each RuntimeStaticAbility can contain multiple RuntimeContinuousEffects.

Effects are applied according to their layer and sublayer order.

Layer 6 / Keyword Abilities:

Keywords like Flying, Deathtouch, etc., are applied after other static effects in layer 6.

Why it matters:
Magic’s layer system ensures that effects like “Creature gets +1/+1” and “Creature becomes a Zombie” are applied in the correct order. This class is the engine that enforces those rules in the runtime game state.

Example Usage:

layers = LayerSystem(game_state)
ec = layers.evaluate(permanent_id)
print(ec.power, ec.toughness, ec.types, ec.abilities)


In short: LayerSystem evaluates all continuous/static effects according to MTG’s official layered rules, giving the current true characteristics of a permanent.

        --- system.py:

        Layered characteristic evaluation (functional style).

Purpose:
This module provides a standalone function to compute a permanent’s characteristics according to MTG’s layered system (layers 1–7), similar to what LayerSystem does in the object-oriented version. It is likely a functional alternative or utility for evaluating characteristics outside the OO LayerSystem.

Key Function: evaluate_characteristics

def evaluate_characteristics(game_state: "GameState", obj_id: int) -> EvaluatedCharacteristics:


Parameters:

game_state: current game state

obj_id: the ID of the permanent to evaluate

Process Overview:

Initialize EvaluatedCharacteristics with the object’s printed/base characteristics.

Apply hardcoded layers 1–3 (supertypes, types, subtypes) via apply_layer1/2/3.

Apply static abilities (layers 4–7):

Collect all static abilities affecting the object

Sort them by sublayer if present (important for Layer 7 P/T ordering)

Apply each effect to the EvaluatedCharacteristics object

Layer 6 applies keyword abilities separately

Return the final EvaluatedCharacteristics.

Important Notes:

Layer 1: supertype changes

Layer 2: type changes

Layer 3: subtype changes

Layer 4: control-changing effects (not shown explicitly)

Layer 5: abilities from static effects

Layer 6: keyword abilities

Layer 7: power/toughness modifiers

Usage Example:

ec = evaluate_characteristics(game_state, permanent_id)
print(ec.power, ec.toughness, ec.abilities)


Key Point:
This function provides a deterministic, snapshot evaluation of a permanent’s characteristics, applying all continuous and static effects without mutating the object itself. It’s especially useful for rules checks, triggers, or UI display.

        --- types.py:

        Container for evaluated permanent characteristics.

Purpose:
Stores the final, computed characteristics of a permanent after applying all continuous effects, static abilities, and MTG layers (1–7). This is what the game uses to determine the actual state of a permanent during play.

Fields (EvaluatedCharacteristics):

power: int — current power after all modifications

toughness: int — current toughness after all modifications

types: set — current types (e.g., Creature, Artifact)

subtypes: set — current subtypes (e.g., Elf, Warrior)

supertypes: set — current supertypes (e.g., Legendary)

colors: set — current colors (e.g., {"W", "U"})

abilities: set — current abilities and keywords (e.g., Flying, Trample)

Usage Example:

from axis3.rules.layers.layersystem import LayerSystem

layer_system = LayerSystem(game_state)
ec = layer_system.evaluate(permanent_id)

print(ec.power, ec.toughness)
print(ec.abilities)


Key Point:
EvaluatedCharacteristics is immutable during evaluation but can be updated by the LayerSystem as each layer and effect is applied. It represents the “real” characteristics that other rules, triggers, and combat calculations will use.

    -- replacement/
        --- apply.py:

        Replacement effect application system.

Purpose:
This module handles replacement effects, which are effects that modify or replace events before they happen in the game (e.g., “If a creature would die, exile it instead”).

Key Function: apply_replacements
def apply_replacements(game_state: "GameState", event: Event) -> Event:


Parameters:

game_state: the current game state containing objects and global replacement effects

event: the event to process

Returns:

A new Event object with all applicable replacements applied, or the original if unchanged.

Process:

Object-specific replacement effects

Checks the object involved in the event (obj_id)

Iterates over its replacement_effects

Applies any that pass their condition

Global replacement effects

Iterates over game_state.replacement_effects

Applies any that pass their condition

Replacement effects do not mutate the original event, but return a new one.

Helper Function: _check_and_apply
def _check_and_apply(eff, event: Event, game_state: "GameState", rt_obj) -> Event | None:


Purpose:
Check a single replacement effect’s condition and apply it if valid.

Behavior:

Returns a new event if the replacement effect applies

Returns None if the effect does not apply

Example Usage
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType

event = Event(type=EventType.ZONE_CHANGE, payload={"obj_id": "42", "from_zone": "BATTLEFIELD", "to_zone": "GRAVEYARD"})
new_event = apply_replacements(game_state, event)


If a replacement effect says “exile instead of graveyard,” new_event.payload["to_zone"] would become EXILE.

✅ Key Points:

Replacement effects are evaluated before the event resolves.

Both object-specific and global replacements are handled.

Effects are conditionally applied, ensuring flexible rule interactions.

This system preserves immutability of events for replayability/logging.

        --- types.py:

        Definition of Replacement Effects

This module defines the runtime representation of replacement effects in Axis3. These are the effects that can replace or modify events as they occur.

ReplacementEffect dataclass
@dataclass
class ReplacementEffect:
    source_id: Optional[int]                # The object that created this effect (None if global)
    applies_to: str                         # Event type this effect applies to (e.g., "zone_change", "draw", "damage")
    condition: Callable[[Dict[str, Any]], bool]   # Function that checks if the effect applies to a given event
    apply: Callable[[Dict[str, Any]], Dict[str, Any]] # Function that returns the modified event

Fields Explained

source_id

Refers to the object (card, token, permanent) that generated this replacement effect.

None indicates a global replacement effect, not tied to a specific object.

applies_to

A string describing the event type the effect can replace, e.g., "zone_change" or "draw".

This is used by apply_replacements to filter which effects are relevant.

condition

A callable that takes the event payload dictionary and returns True if the replacement should apply.

Example: Only replace zone changes for a specific object ID.

apply

A callable that takes the event payload and returns a new payload with the replacement applied.

Example: "dies_exile_instead" effect would change "to_zone" from GRAVEYARD to EXILE.

Example Usage
from axis3.state.zones import ZoneType as Zone

repl_effect = ReplacementEffect(
    source_id=42,
    applies_to="zone_change",
    condition=lambda e: e["obj_id"] == 42 and e["to_zone"] == Zone.BATTLEFIELD,
    apply=lambda e: {**e, "enters_tapped": True}
)


This effect would make a specific object enter the battlefield tapped.

✅ Key Points:

Encapsulates replacement logic at runtime.

Supports both object-specific and global effects.

Works seamlessly with apply_replacements to produce modified events before resolution.

Enables complex interactions like "if a creature would die, exile it instead" or "draw an extra card instead."

    -- sba/
        --- checker.py:

        State-Based Actions (SBAs) Runner

This module is responsible for evaluating and enforcing state-based actions in Axis3. These are checks that happen continuously in a Magic-like game to ensure the game state is consistent according to rules.

run_sbas function
def run_sbas(game_state: "GameState"):
    """
    Run state-based actions until the game state stabilizes.
    """
    
    while True:
        changed = False

        # 1️⃣ Check for game loss
        for player in game_state.players:
            if player.life <= 0:
                player.dead = True
                return

        # 2️⃣ Check various state-based actions
        if check_lethal_damage(game_state):
            changed = True

        if check_zero_toughness(game_state):
            changed = True

        if check_tokens(game_state):
            changed = True

        if check_legend_rule(game_state):
            changed = True

        # 3️⃣ Stop once no further changes occur
        if not changed:
            return

What It Does

Loop until stable:
SBAs are applied repeatedly until no further changes occur. This ensures cascading effects (e.g., creatures dying due to zero toughness) are fully resolved.

Checks included:

Player life ≤ 0: Marks the player as dead.

Lethal damage: Detects damage that should destroy creatures.

Zero toughness: Creatures with toughness ≤ 0 die.

Token creation/deletion rules: Ensures token permanents are handled correctly.

Legend rule: Ensures only one legendary permanent of a given name can exist under a player’s control.

changed flag:

Any modification to the game state sets changed = True.

The loop continues until the game stabilizes (no further changes).

Integration

Called after events are applied to ensure the game state respects rules.

Works closely with the EventBus and atomic events to handle cascading interactions.

✅ Key Points:

Ensures continuous enforcement of game rules.

Resolves lethal damage, zero toughness, token management, and legendary conflicts.

Loops until the game state stabilizes, preventing invalid states from persisting.

        --- rules.py:

        Detailed Explanation

This module implements the state-based action (SBA) rules for Axis3. Each function checks a specific condition required by the official Magic: The Gathering rules and publishes events to fix the game state if necessary.

1️⃣ check_lethal_damage
def check_lethal_damage(game_state) -> bool:


Purpose: Destroy creatures that have received lethal damage (damage ≥ toughness).

Process:

Iterate over all objects on the battlefield.

Skip non-creatures.

Evaluate current toughness via layers.

If damage ≥ toughness, publish a zone change event moving the creature to the graveyard.

Returns: True if any creatures were affected.

2️⃣ check_zero_toughness
def check_zero_toughness(game_state) -> bool:


Purpose: Destroy creatures whose toughness is 0 or less.

Process:

Similar to check_lethal_damage, but uses evaluated toughness only.

Publishes a zone change to the graveyard if toughness ≤ 0.

Returns: True if any creatures were moved.

3️⃣ check_tokens
def check_tokens(game_state) -> bool:


Purpose: Remove token objects that are no longer on the battlefield (they “cease to exist”).

Process:

Iterate over all objects.

Skip non-tokens and tokens still on the battlefield.

Publish a zone change event with to_zone=None, which removes the token.

Returns: True if any tokens were removed.

4️⃣ check_legend_rule
def check_legend_rule(game_state) -> bool:


Purpose: Enforce the Legendary rule (704.5j), which states that a player cannot control multiple legendary permanents with the same name.

Process:

For each player, group legendary permanents on the battlefield by name.

If multiple objects share the same name:

Keep the first one.

Send the rest to the graveyard using a zone change event.

Returns: True if any legendary permanents were removed.

Integration

These SBAs are called repeatedly in run_sbas until the game state stabilizes.

They ensure that the game adheres to rules 704.5a–j of Magic: The Gathering.

All actions are represented via zone change events, which means the rest of the game engine (triggers, replacement effects, etc.) reacts naturally.

✅ Key Points

Lethal damage and zero toughness are separate checks.

Tokens outside battlefield are removed automatically.

Legend rule is currently automated: the first permanent is kept, the rest go to the graveyard.

Each SBA returns a bool indicating if it changed the game state, allowing the orchestrator to loop until stable.

This module, combined with checker.py, forms the core SBA enforcement in Axis3.

    -- stack/
        --- item.py:

        Explanation

This module defines the StackItem class, which represents a single object on the stack in Axis3 (spells and abilities).

Class: StackItem
class StackItem:


Represents a spell or ability currently on the stack. Stack items can be:

A spell (cast from hand or battlefield):

Identified by obj_id (RuntimeObject ID).

Has a controller (the player who cast it).

Optional x_value for variable-cost spells (like X in {X}{G}).

A triggered ability:

Stored in triggered_ability (instance of RuntimeTriggeredAbility).

An activated ability:

Stored in activated_ability (instance of RuntimeActivatedAbility).

Constructor
def __init__(self, obj_id=None, controller=None, x_value=None, triggered_ability=None, activated_ability=None):


Initializes a stack item with one of three types.

Only one type should be set per item.

Helper Methods
def is_triggered_ability(self) -> bool


Returns True if the stack item is a triggered ability.

def is_activated_ability(self) -> bool


Returns True if the stack item is an activated ability.

def is_spell(self) -> bool


Returns True if the stack item is a spell (not a triggered or activated ability).

Usage

StackItems are stored in the GameState.stack.

The orchestrator resolves the stack by checking each item’s type and executing the correct game logic (spell resolution, triggered abilities, activated abilities).

This class provides a unified interface for all objects that go on the stack, allowing Axis3 to handle stack resolution generically.

        --- resolver.py:

        Explanation

This module defines the stack and how the game resolves items on it in Axis3. It combines stack management with resolution logic for spells and abilities.

Class: Stack
class Stack:


Represents the game stack, which is LIFO (last-in, first-out).

Key methods:

push(item: StackItem): Push an item onto the stack.

pop() -> StackItem: Remove and return the top item.

peek() -> StackItem: View the top item without removing it.

is_empty() -> bool: Check if the stack is empty.

Function: push_to_stack(game_state, stack_item)
def push_to_stack(game_state: "GameState", stack_item: StackItem):


Adds a spell or ability onto the game's stack.

Ensures the GameState has a Stack instance.

Function: resolve_top_of_stack(game_state)
def resolve_top_of_stack(game_state: "GameState"):


Resolves the topmost stack item (LIFO). Handles different types:

Triggered Ability

if item.is_triggered_ability():
    resolve_runtime_triggered_ability(game_state, item.triggered_ability)


Executes the ability's effect and runs state-based actions (SBAs).

Activated Ability

if item.is_activated_ability():
    item.activated_ability.effect(game_state)


Executes the ability effect. Costs and replacement effects may also apply.

Permanent or Land

Checks if the object is a permanent (Creature, Artifact, Enchantment, Planeswalker, Land).

Determines its destination zone:

Permanents → BATTLEFIELD

Non-permanents → GRAVEYARD after resolution

Tokens

Non-permanent tokens disappear instead of going to a zone.

Zone Change

zone_change.apply_zone_change(game_state, event)


Applies the move with replacement effects considered.

Lands

ETB tapped/untapped effects handled via replacement effects applied above.

Update Game State

SBAs are run to stabilize the game state after resolution.

Function: resolve_stack(game_state)
def resolve_stack(game_state: "GameState"):


Resolves all items on the stack until empty.

Simply calls resolve_top_of_stack repeatedly.

✅ Key Points

Integrates replacement effects, SBAs, and triggered/activated abilities.

Provides LIFO resolution for the stack.

Handles permanents, spells, lands, and tokens differently.

Central to spell resolution and game flow in Axis3.

This module is essentially the engine for resolving actions on the stack in a Magic-like game.

    -- triggers/
        --- registry.py:

        Explanation

This module manages triggers in the game: both object-specific and global triggers.

Trigger Registry
_trigger_registry = []


A global list of triggers that are always monitored.

Function: register_trigger(trigger)
def register_trigger(trigger):


Adds a trigger to the global _trigger_registry.

These triggers are checked on all events relevant to them.

Function: check_triggers(game_state, event)
def check_triggers(game_state, event):


Called whenever an event is published.

Checks both object triggers and global triggers.

Step 1: Object-specific triggers
for obj_id, rt_obj in game_state.objects.items():
    for trig in getattr(rt_obj.axis2, "triggers", []):
        if trig.event == event.type:
            rta = RuntimeTriggeredAbility(source_id=rt_obj.id, controller=rt_obj.controller, axis2_trigger=trig)
            push_to_stack(game_state, StackItem(triggered_ability=rta))


Iterates all objects on the battlefield.

Fires triggers matching the current event type.

Creates a RuntimeTriggeredAbility and pushes it to the stack.

Step 2: Global triggers
for trig in _trigger_registry:
    if trig.event == event.type:
        rta = RuntimeTriggeredAbility(source_id=None, controller=trig.controller, axis2_trigger=trig)
        push_to_stack(game_state, StackItem(triggered_ability=rta))


Iterates global triggers in _trigger_registry.

Fires triggers matching the event type.

Pushes the resulting triggered abilities to the stack.

✅ Key Points

Separates object-specific and global triggers.

All triggered abilities are placed on the stack to follow normal resolution rules.

Ensures that the game engine correctly handles automatic and conditional reactions to events.

This module essentially acts as the central “watcher” for all triggers and integrates them into the stack system.

        --- runtime.py:

        Explanation

This module handles runtime triggered abilities—the abilities created when a trigger fires and is placed on the stack.

Class: RuntimeTriggeredAbility
class RuntimeTriggeredAbility:
    def __init__(self, source_id: int, controller: int, axis2_trigger):
        self.source_id = source_id
        self.controller = controller
        self.axis2_trigger = axis2_trigger


Represents a triggered ability at runtime.

Fields:

source_id: The object that caused the trigger (None for global triggers).

controller: The player who controls the ability.

axis2_trigger: The original Axis2 trigger object, which contains the effect text and conditions.

Function: resolve_runtime_triggered_ability
def resolve_runtime_triggered_ability(game_state: "GameState", rta: RuntimeTriggeredAbility):


Resolves a triggered ability immediately (simplified model; in a full MTG engine, it would go through the stack normally).

Steps:

Extract effect_text from the Axis2 trigger.

Parse simple effects like "draw a card" or "lose 1 life".

Call the corresponding atomic rule:

apply_draw(game_state, rta.controller, 1)
apply_life_change(game_state, rta.controller, -1)


TODO: The stub currently handles only very simple text effects. A full implementation would parse all possible trigger effects.

✅ Key Points

Converts Axis2 triggers into runtime-triggered abilities.

In Phase 2 of the game engine, this allows immediate resolution of simple triggers.

Works together with registry.py and resolver.py:

registry.py pushes triggered abilities to the stack when an event fires.

resolver.py calls resolve_runtime_triggered_ability when a triggered ability is on top of the stack.

This module effectively bridges static trigger definitions (Axis2) with dynamic, runtime game resolution.

        --- types.py:

        Explanation

This module implements a runtime registry for triggers, allowing the game engine to notify subscribed objects or effects when certain events occur.

Class: TriggerRegistry
class TriggerRegistry:


Keeps track of event subscriptions at runtime.

Used by the EventBus to notify relevant triggers whenever an event is published.

Internal Data Structure
self._registry: Dict[str, List[Callable[[Event], None]]]


Maps event type strings to lists of callback functions.

Each callback is a function that takes an Event object as a parameter.

Example: "draw" → [callback1, callback2].

Methods
1. register
def register(self, event_type: str, callback: Callable[[Event], None]):


Subscribes a callback function to a specific event type.

If no callbacks exist yet for this event type, a new list is created.

2. unregister
def unregister(self, event_type: str, callback: Callable[[Event], None]):


Removes a previously registered callback for an event type.

Cleans up empty lists to avoid memory leaks.

3. notify
def notify(self, event: Event):


Called by EventBus whenever an event occurs.

Invokes all callbacks registered for event.type.

Ensures that all triggers that care about the event get a chance to respond.

✅ Key Points

Provides a centralized way to manage runtime trigger subscriptions.

Works seamlessly with the EventBus:

EventBus publishes events → TriggerRegistry.notify() → registered callbacks execute.

Enables modular, decoupled trigger handling in the game engine.

Each callback could push a triggered ability onto the stack, update state, or perform side effects.

This is the final piece of the Axis3 runtime trigger system, linking events → registry → stackable triggered abilities.

    --orchestrator.py:

    Central game engine controller.

Purpose: Acts as the main orchestrator for the Axis3 game engine, handling events, triggers, replacement effects, SBAs, and the stack in a unified flow.

Key Components & Responsibilities:

GameOrchestrator class: encapsulates the game loop and event management.

_handle_event(event) — Core event handler:

Applies replacement effects.

Checks and queues triggers.

Executes atomic game events (like moving cards, damage, counters).

Runs state-based actions (SBAs), e.g., creatures with 0 toughness die.

Stack helpers:

push_to_stack(stack_item) — Adds an item (spell/ability) to the stack.

resolve_top_of_stack() — Resolves the top stack item.

resolve_full_stack() — Resolves the entire stack iteratively.

Event helpers:

publish_event(event) — Sends an event into the orchestrator’s event bus.

Usage:

Provides a single interface for game progression.

Ensures proper ordering of effects, triggers, and resolution according to game rules.

Central point for integrating stack management, replacement effects, triggers, and SBAs in a coordinated way.

In short: this file coordinates the full runtime flow of the game, serving as the “brain” that enforces game rules.

- state/
    -- characteristics.py:

    Runtime representation of a card’s printed/base characteristics.

Purpose: Stores the core properties of a card or permanent as defined on the card face. These are the "starting values" before any continuous effects, layers, or game state modifications are applied.

Key class:

RuntimeCharacteristics — A dataclass containing:

name, mana_cost → Card name and mana cost.

types, supertypes, subtypes → Card type line info.

colors → Card colors (e.g., ["W", "U"]).

power, toughness → Creature stats (None if not a creature).

loyalty → Planeswalker loyalty, optional.

counters → Dict of counters on the object (e.g., {"+1/+1": 2}).

keywords → List of keyword abilities (e.g., ["flying"]).

abilities → List of other static abilities (as strings).

Usage:

This is read-only base data. The engine calculates current values using layers and continuous effects (axis3.rules.layers) derived from these base characteristics.

Acts as the foundation for evaluated characteristics for use in rules, combat, and ability resolution.

It’s essentially the “printed card” snapshot for the runtime engine.

    -- game_state.py:

    Central runtime representation of the game state.

Purpose: Encapsulates all mutable game information for a match: players, permanents, zones, stack, turn/phase info, effects, and layers. This is the backbone of the Axis3 engine.

Key classes:

Phase / Step (Enums)

Represent turn phases and steps, e.g., BEGINNING, COMBAT, DRAW, DECLARE_ATTACKERS.

Used to track game progression and when certain triggers/abilities can occur.

PlayerState

Stores individual player zones (library, hand, battlefield, graveyard, exile, command).

Tracks mana pool, life total, and max hand size.

TurnState

Tracks the active player, priority player, current phase & step, turn number.

Tracks stack priority mechanics, like whether the stack has been empty since last priority.

GameState

Players & objects: Holds PlayerState list and a dict of RuntimeObjects representing cards/permanents.

Stack & EventBus: Contains the game stack and event system for triggers and responses.

Replacement & Continuous Effects: Lists of effects currently applied to the game.

LayerSystem: Handles continuous effect layering (power/toughness, abilities, type changes, etc.).

Methods:

zone_list(controller_id, zone) → returns the list of object IDs for a given player's zone.

__post_init__() → initializes the EventBus and LayerSystem.

Usage:

The core object passed to all rules, abilities, and resolution functions.

Everything in the game references or modifies GameState to maintain consistency.

In short, GameState is the authoritative snapshot of the game at any moment, integrating players, objects, zones, stack, effects, and turn progression.

    -- objects.py:

    Defines the runtime representations of all in-game objects.

Purpose: Encapsulates all the mutable properties of cards, tokens, permanents, and spells, including both Axis1/Axis2 metadata and dynamic runtime state like counters, tapped status, and zones. This is the core building block for all game interactions.

Key components:

RuntimeObjectId

Alias for str, used as a unique identifier for each runtime object.

RuntimeObject (base class)

Base class for anything that can exist in the game: permanents, spells, tokens, ability objects.

Key fields:

id, owner, controller, zone — ownership/control and location.

axis1_card, axis2_card — references to pre-runtime card data.

characteristics — P/T, types, colors, abilities, etc.

tapped, damage, counters — dynamic runtime state.

is_token — flag for tokens.

Methods: has_type(t), is_creature(), is_spell().

RuntimePermanent (subclass of RuntimeObject)

Represents permanents on the battlefield.

Adds summoning_sick flag.

Method can_attack() checks standard attacking restrictions.

RuntimeSpell (subclass of RuntimeObject)

Represents a spell on the stack.

Holds chosen modes, targets, and mana paid.

Overrides is_spell() to always return True.

RuntimeToken (subclass of RuntimePermanent)

Represents token permanents created by spells or abilities.

Adds token_name field.

Usage:

Every card, token, or spell in play is represented as a RuntimeObject or one of its subclasses.

Enables layered rules, stack resolution, and ability tracking by providing a unified interface to all in-game objects.

In short: this file defines all runtime entities and their mutable state in Axis3.

    -- player_data.py:

    Represents per-turn runtime state for a single player.

Purpose: Tracks dynamic player-specific data that resets or changes frequently during a turn, separate from the more persistent PlayerState (library, hand, battlefield, life total).

Key fields:

mana_pool: dict — Tracks available mana of each color (W, U, B, R, G).

priority: bool — Whether the player currently has priority to cast spells or activate abilities.

has_played_land: bool — Whether the player has played a land this turn (important for land drop rules).

Usage:

Useful for turn-based mechanics, such as casting restrictions, mana spending, and tracking priority.

Typically instantiated at the start of each turn or used inside TurnState/PlayerState to manage temporary per-turn flags.

In short: this file encapsulates the per-turn, mutable data of a player that the game engine needs to enforce rules and track temporary states.

    -- zones.py:

    Defines zones in the game and their properties.

Purpose: Provides a central place for the game engine to identify different card/ability locations and properties like visibility and order sensitivity.

Key components:

ZoneType (Enum) — Lists all possible zones a card/object can occupy:

LIBRARY, HAND, BATTLEFIELD, GRAVEYARD, EXILE, STACK, COMMAND.

PUBLIC_ZONES — Zones visible to all players (battlefield, graveyard, exile, stack, command).

ORDERED_ZONES — Zones where the order of objects matters (library, stack).

is_public_zone(zone) — Returns True if the zone is public.

is_ordered_zone(zone) — Returns True if the zone is ordered.

Usage:

Determine visibility rules for objects.

Determine interaction rules, e.g., top/bottom of library or stack resolution.

Provides type-safe zone management throughout Axis3.

In short: this file standardizes zone definitions and their properties, essential for enforcing game mechanics.

- translate/
    -- ability_builder.py:

    Translates Axis2 abilities into runtime objects:

Purpose: Converts all Axis2-level abilities and effects of a card into runtime-ready objects and attaches them to the corresponding RuntimeObject. This makes them usable by the game engine during play.

What it does:

Triggered Abilities:

Wraps each Axis2 trigger into a RuntimeTriggeredAbility.

Subscribes a callback to the game’s EventBus for the relevant event type (like "enters_battlefield" or "dies").

When the event occurs, a StackItem with the triggered ability is pushed to the stack.

Activated Abilities:

Wraps each Axis2 activated ability into a RuntimeActivatedAbility.

Stores it directly on the RuntimeObject for later activation by the player.

Static / Continuous Effects:

Converts Axis2 static effects into RuntimeContinuousEffect objects.

Stores them on the object so they can be applied during layer evaluation (power/toughness modifications, granted abilities, etc.).

Key idea: This module acts as a bridge from the design-time card definitions (Axis2) to runtime-ready abilities that the game engine can execute, push to the stack, or evaluate continuously.

It’s basically the “ability factory” for the runtime system.

    -- activated_builder.py:

    Builds runtime activated abilities for a RuntimeObject.

Purpose: Converts Axis2 activated abilities into runtime-ready RuntimeActivatedAbility objects that can be activated by players and either resolve immediately (mana abilities) or be pushed to the stack.

What it does:

Loops through all Axis2 activated abilities on the card (rt_obj.axis2_card.activated_abilities).

Determines if the ability is a mana ability (is_mana_ability).

Wraps the raw Axis2 effect in a runtime callable (effect) that matches the RuntimeActivatedAbility interface.

Creates a RuntimeActivatedAbility object with:

source_id → the object ID

controller → who can activate it

cost → the Axis2-defined cost

effect → the wrapped callable

Overrides the activate method to:

Immediately resolve the effect if it’s a mana ability.

Otherwise, push a StackItem containing the activated ability onto the game stack for later resolution.

Stores the runtime ability on the object (rt_obj.runtime_activated_abilities) and provides a convenience alias invoke.

Key idea: This module prepares activated abilities so they behave correctly at runtime, respecting costs, stack interaction, and special rules like mana abilities resolving instantly.

Essentially, it’s the runtime “activation engine” for object abilities.

    -- continuous_builder.py:

    Builds runtime continuous (static) effects for a RuntimeObject.

Purpose: Converts Axis2-defined continuous effects into runtime-ready RuntimeContinuousEffect objects that the layer system can apply automatically. These effects modify power/toughness, grant/remove abilities, or change other characteristics dynamically.

What it does:

Loops through all Axis2 continuous effects on the object (axis2_card.continuous_effects).

For each effect, checks its kind (e.g., global_pt_modifier, aura_pt_and_ability) to determine behavior.

Wraps the effect logic in callable functions:

applies_to(gs, obj_id) → determines which objects are affected.

modify_power(gs, obj_id, current) → how to adjust power.

modify_toughness(gs, obj_id, current) → how to adjust toughness.

grant_abilities(gs, obj_id, ability_set) → adds keywords if needed.

Creates RuntimeContinuousEffect objects with the proper layer/sub-layer:

Layer 6 → ability adding/removing

Layer 7b → power/toughness modifications

Appends them to game_state.continuous_effects for evaluation during the layer system.

Key idea: This module translates declarative Axis2 static effects into runtime objects that integrate seamlessly with the game’s layer-based system, ensuring creatures and permanents update characteristics correctly.

Essentially, it’s the bridge between static card definitions and the dynamic layer evaluation engine.

    -- loader.py:

    Runtime object & game state builder.

Purpose: Bridges Axis1/Axis2 card definitions into a fully initialized Axis3 runtime game state with proper characteristics, abilities, and effects. It handles object IDs, ownership, zones, and integrates all runtime behaviors.

Key functions:

_next_id() → Generates unique runtime object IDs.

derive_base_characteristics(axis1_card) → Converts an Axis1 card face into RuntimeCharacteristics (name, mana cost, types, colors, P/T, abilities).

create_runtime_object(axis1_card, axis2_card, owner_id, zone, game_state) →

Builds a RuntimeObject with Axis1/Axis2 integration.

Registers triggered abilities, activated abilities, continuous/static effects, and replacement effects.

build_game_state_from_decks(player1_deck_axis1, player2_deck_axis1, axis2_builder) →

Creates a GameState with two players, empty stacks, and event bus.

Converts Axis1 decks into RuntimeObjects for each player and shuffles libraries.

Returns a fully initialized GameState ready for simulation.

Key idea: This module is essentially the loader/factory for the Axis3 engine, turning declarative card definitions into live game objects with all runtime behaviors wired in.

It’s the entry point for setting up a game with full card interactions, stack management, and layer-based effects.

    -- replacement_builder.py:

    Runtime replacement effects builder.

Purpose: Converts Axis2 card replacement effect definitions into runtime ReplacementEffect objects and registers them in the GameState. These effects intercept and modify events before they fully resolve.

Key function:

build_replacement_effects_for_object(game_state, rt_obj)

Iterates through rt_obj.axis2_card.replacement_effects.

For each effect type (enters_tapped, enters_with_counters, dies_exile_instead), it creates a ReplacementEffect with:

applies_to → Event type it reacts to (currently "zone_change").

condition → Checks if the replacement should trigger for the given object and event.

apply → Function that modifies the event (e.g., adding counters, changing the zone, marking as tapped).

Appends the effect to game_state.replacement_effects.

Key idea: This module is the bridge from declarative Axis2 replacement effects to runtime effects, allowing the engine to automatically adjust zone changes (like entering tapped, adding counters, or exile replacement) before they fully resolve.

It ensures that any replacement rules defined on cards are automatically applied when the object moves zones or dies.