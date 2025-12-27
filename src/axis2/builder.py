import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from axis1.schema import Axis1Card  # Axis 1 schema
from axis2.schema import (
    Axis2Card,
    CastSpellAction,
    PlayLandAction,
    ActivateAbilityAction,
    SpecialAction,
    TimingRules,
    CostRules,
    TargetingRules,
    TargetingRestriction,
    TurnPermissions,
    VisibilityConstraints,
    Trigger,
    ZonePermissions,
    GlobalRestriction,
    Condition,
    ActionReplacement,
    ActionPrevention,
    ActionModifier,
    MandatoryAction,
    LimitRule,
    VisibilityRule,
    StaticEffect,
    ReplacementEffect,
)
from axis2.rules import targeting as targeting_rules
from axis2.rules import effects as effects_rules
from axis2.rules import timing as timing_rules
from axis2.rules import costs as cost_rules
from axis2.rules import permissions as permission_rules
from axis2.rules import restrictions as restriction_rules
from axis2.rules import keywords as keywords_rules
from axis2.rules import static_effects as static_effects_rules
from axis2.rules import replacement_effects as replacement_rules
from axis2.rules import etb_replacement as etb_replacement_rules
from axis2.rules import modes as modes_rules
from axis2.rules import activated_abilities as activated_abilities_rules


# ------------------------------------------------------------
# GAME STATE INTERFACE (Axis 3 placeholder)
# ------------------------------------------------------------

@dataclass
class GameState:
    """
    Minimal placeholder for game state.

    Extend this with:
    - players
    - zones
    - effects
    - turn structure
    - stack
    - timestamps
    """
    active_player_id: str
    priority_player_id: str
    turn_phase: str
    turn_step: str
    battlefield: List[Any]
    graveyards: Dict[str, List[Any]]
    hands: Dict[str, List[Any]]
    exile: List[Any]
    command_zone: List[Any]
    stack: List[Any]
    continuous_effects: List[Any]
    replacement_effects: List[Any]
    global_restrictions: List[Any]


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def _is_spell(axis1_card: Axis1Card) -> bool: 
    if "Token" in axis1_card.characteristics.card_types: 
        return False 
    return any(t in axis1_card.characteristics.card_types for t in [ "Creature", "Instant", "Sorcery", "Planeswalker", "Artifact", "Enchantment", "Battle" ])


def _is_land(axis1_card: Axis1Card) -> bool:
    return "Land" in axis1_card.characteristics.card_types


def _base_cast_zones(axis1_card: Axis1Card) -> List[str]:
    """
    Default cast zones; can be extended by permissions (flashback, escape, etc.).
    """
    zones = ["Hand"]
    # Note: extra zones (Graveyard, Exile, Command) are handled via permissions
    return zones


def _base_play_land_zones(axis1_card: Axis1Card) -> List[str]:
    return ["Hand"]


def _derive_zone_permissions(axis1_card: Axis1Card, game_state: GameState) -> ZonePermissions:
    """
    Basic zone permissions based on type + Axis2 permissions engine.
    """
    perms: Dict[str, List[str]] = {
        "Hand": [],
        "Graveyard": [],
        "Battlefield": [],
        "Exile": [],
        "Command": [],
    }

    # Base spell / land permissions from hand
    if _is_spell(axis1_card):
        perms["Hand"].append("cast_spell")

    if _is_land(axis1_card):
        perms["Hand"].append("play_land")

    # On battlefield: abilities & special actions
    perms["Battlefield"].append("activate_ability")
    perms["Battlefield"].append("special_actions")

    # Extend with permissions engine (flashback, escape, etc.)
    permissions_obj = permission_rules.derive_permissions(axis1_card, game_state)
    perm_rules = permissions_obj.permissions

    if "may_cast_from_graveyard" in perm_rules:
        perms["Graveyard"].append("cast_spell")

    if "may_cast_from_exile" in perm_rules:
        perms["Exile"].append("cast_spell")

    if "may_cast_from_command" in perm_rules:
        perms["Command"].append("cast_spell")

    if "may_play_lands_from_graveyard" in perm_rules:
        perms["Graveyard"].append("play_land")

    return ZonePermissions(permissions=perms)


def _derive_global_restrictions(game_state: GameState) -> List[GlobalRestriction]:
    """
    Convert high-level global effects (Rule of Law, etc.) into Axis2 global restrictions.
    Currently mirrors entries from game_state.global_restrictions.
    """
    restrictions: List[GlobalRestriction] = []

    for effect in game_state.global_restrictions:
        restrictions.append(
            GlobalRestriction(
                applies_to=effect.get("applies_to", "all"),
                restriction=effect.get("restriction", "")
            )
        )

    return restrictions


def _derive_limits(axis1_card: Axis1Card, game_state: GameState) -> List[LimitRule]:
    """
    Limits include:
    - once per turn activations
    - commander tax
    - spell-per-turn limits
    - land-per-turn limits
    """
    limits: List[LimitRule] = []

    # Land play limit (global, but surfaced here for convenience)
    if _is_land(axis1_card):
        limits.append(
            LimitRule(
                action="play_land",
                limit_type="extra_land_per_turn",
                dynamic=True,
                tracking_per_player=True,
                base_limit=1,
            )
        )

    # TODO: Add commander tax, once-per-turn, spell-per-turn, etc.

    return limits


def _derive_visibility_constraints(axis1_card: Axis1Card) -> VisibilityRule:
    """
    Handle face-down cards, hidden zones, randomization, etc.
    """
    # For now, assume normal face-up cards.
    return VisibilityRule(
        face_down_objects={
            "cannot_be_targeted": False,
            "cannot_be_revealed_except_by_effects": False,
        },
        hidden_zones=[],
        random_selection=False,
    )


def _derive_action_modifiers(
    axis1_card: Axis1Card,
    game_state: GameState,
    static_effects: List[StaticEffect]
) -> List[ActionModifier]:
    """
    Handle effects like:
    - cost reduction/increase for specific card types
    - flash granted by external effects

    Driven by continuous_effects in game_state + static_effects on the card.
    """
    modifiers: List[ActionModifier] = []

    # Example: map continuous effects of type cost_reduction / cost_increase
    for effect in static_effects:
        if effect.kind in ("cost_reduction", "cost_increase"):
            modifiers.append(
                ActionModifier(
                    original=effect.kind,
                    modification=effect.subject,
                    layer=0,
                    order=0,
                )
            )

    # You can later add more mappings here.

    return modifiers


def _derive_action_replacements(axis1_card: Axis1Card, game_state: GameState, replacement_effects: List[ReplacementEffect]) -> List[ActionReplacement]:
    """
    Handle structured replacements of actions:
    - "cast as though it had flash"
    - "can't be countered" style interaction changes
    """
    replacements: List[ActionReplacement] = []

    for eff in replacement_effects:
        replacements.append(
            ActionReplacement(
                type=eff.get("type", ""),
                subject=eff.get("subject", ""),
                event=eff.get("event", ""),
                replacement=eff.get("replacement", ""),
            )
        )

    return replacements


def _derive_action_preventions(axis1_card: Axis1Card, game_state: GameState, static_effects: List[StaticEffect]) -> List[ActionPrevention]:
    """
    Handle prevention of actions:
    - "can't cast more than one spell per turn"
    - "players can't activate abilities"
    """
    preventions: List[ActionPrevention] = []

    # Example: from global restrictions or static effects
    for eff in static_effects:
        if eff.kind in ("cant_cast_spells", "one_spell_per_turn", "cant_activate_abilities"):
            preventions.append(
                ActionPrevention(
                    type=eff.kind,
                    subject=eff.subject,
                    value=eff.value,
                )
            )

    return preventions


def _derive_mandatory_actions(axis1_card: Axis1Card, game_state: GameState, static_effects: List[StaticEffect]) -> List[MandatoryAction]:
    """
    Handle mandatory actions:
    - "must attack each combat if able"
    """
    mandatory: List[MandatoryAction] = []

    for eff in static_effects:
        if eff.kind in ("attack_each_combat_if_able", "block_each_combat_if_able"):
            mandatory.append(
                MandatoryAction(
                    type=eff.kind,
                    subject=eff.subject,
                    value=eff.value,
                )
            )

    return mandatory


def _derive_choice_constraints(axis1_card):
    """
    Handle things like:
    - distinct modes for modal spells
    - random targets for some chaotic effects
    """
    oracle = axis1_card.faces[0].oracle_text or ""

    if "as this creature enters" in oracle.lower() and "primal clay" in oracle.lower(): 
        return ["choose_exactly_1_form"]

    m = modes_rules.MODAL_HEADER.search(oracle)
    if not m:
        return []

    choice = m.group(1).lower()
    if choice == "one":
        return ["choose_exactly_1_mode"]
    if choice == "two":
        return ["choose_exactly_2_modes"]
    if choice == "one or more":
        return ["choose_at_least_1_mode"]
    if choice == "any number":
        return ["choose_any_modes"]

    return []

def _derive_conditions(axis1_card: Axis1Card) -> List[Condition]:
    """
    General conditions attached to actions:
    - "if you control an artifact"
    - "if your life total >= 10"
    """
    conditions: List[Condition] = []
    # TODO: parse these from oracle text or Axis1 rules_tags / intrinsic_rules.
    return conditions


# ------------------------------------------------------------
# ACTION BUILDERS
# ------------------------------------------------------------

def _build_cast_spell_action(axis1_card: Axis1Card, game_state: GameState) -> CastSpellAction:

    # Lands are never spells — they are played, not cast
    if "Land" in axis1_card.characteristics.card_types:
        return CastSpellAction(allowed=False)

    # Not a spell → cannot cast
    if not _is_spell(axis1_card):
        return CastSpellAction(allowed=False)

    # 1. Timing rules (instant/sorcery/flash/etc.)
    timing = timing_rules.derive_timing(axis1_card, game_state)

    # 2. Zones you can cast from (Hand by default; others via ZonePermissions/permissions)
    zones = _base_cast_zones(axis1_card)

    # 3. Costs (mana, alternative, reductions, increases)
    costs = cost_rules.derive_cost(axis1_card, game_state)

    # 4. Permissions (flashback, escape, aftermath, etc.)
    permissions_obj = permission_rules.derive_permissions(axis1_card, game_state)
    permissions = permissions_obj.permissions

    # 5. Restrictions (cast only during your turn, etc.)
    restrictions_obj = restriction_rules.derive_restrictions(axis1_card, game_state)
    restrictions = restrictions_obj.restrictions

    # ------------------------------------------------------------
    # 6. Targeting rules
    #    Modal spells NEVER have cast-time targets.
    #    Only chosen modes determine targeting (Axis3).
    # ------------------------------------------------------------
    oracle_text = axis1_card.faces[0].oracle_text or ""
    mode_choice, modes = modes_rules.parse_modes(oracle_text, game_state)

    if modes:
        # Modal spell → no cast-time targets
        targeting_rules_obj = TargetingRules(
            required=False,
            min=0,
            max=0,
            legal_targets=[],
            restrictions=[],
            replacement_effects=[],
        )
    else:
        # Normal spell → use spell-text targeting
        raw_spell_text = getattr(axis1_card.faces[0], "spell_text", "") or oracle_text

        # Remove reminder text in parentheses
        spell_text = re.sub(r"\([^)]*\)", "", raw_spell_text)
        targeting_rules_obj = targeting_rules.derive_targeting_from_spell_text(spell_text, game_state)

    # 7. State restrictions (summoning sickness, tapped, etc. — Axis3 will refine)
    state_restrictions: List[str] = []

    # 8. Turn permissions (controller-only by default)
    turn_permissions = TurnPermissions(
        controller_only=True,
        opponent_only=False,
    )

    # 9. Visibility (face-down, randomized, etc.)
    visibility_constraints = VisibilityConstraints(
        revealed=False,
        randomized=False,
    )

    # 10. Build final CastSpellAction
    return CastSpellAction(
        allowed=True,
        timing=timing,
        zones=zones,
        costs=costs,
        restrictions=restrictions,
        permissions=permissions,
        targeting_rules=targeting_rules_obj,
        state_restrictions=state_restrictions,
        turn_permissions=turn_permissions,
        visibility_constraints=visibility_constraints,
    )

def _build_play_land_action(axis1_card: Axis1Card, game_state: GameState) -> PlayLandAction:

    if not _is_land(axis1_card):
        return PlayLandAction(allowed=False)

    zones = _base_play_land_zones(axis1_card)

    return PlayLandAction(
        allowed=True,
        phases=["main"],
        requires_priority=False,
        limit_per_turn=1,
        dynamic_limit_conditions=[
            {
                "condition": "extra_land_permission_effect",
                "adjust": "+1",
            }
        ],
        zones=zones,
        restrictions=[],
        permissions=[],
        state_restrictions=["cannot_if_field_full"],
        turn_permissions=TurnPermissions(controller_only=True),
    )

def _build_activate_ability_actions(axis1_card: Axis1Card, game_state: GameState) -> List[ActivateAbilityAction]:
    """
    Build ActivateAbilityAction objects from Axis1 activated_abilities.
    Supports:
      - {T}
      - {mana}
      - custom costs like Waterbend {X}
      - restrictions (e.g., "Activate only as a sorcery")
      - permissions (e.g., "without paying its mana cost")
    """
    actions: List[ActivateAbilityAction] = []

    abilities = getattr(axis1_card.faces[0], "activated_abilities", [])
    oracle = (axis1_card.faces[0].oracle_text or "").lower()

    for ability in abilities:
        cost_text = ability.cost
        effect_text = ability.effect

        # ------------------------------------------------------------
        # FILTER OUT NON-ABILITIES
        # ------------------------------------------------------------

        # 1. Skip reminder text or theme text (parentheses)
        if "(" in effect_text and ")" in effect_text:
            continue

        # 2. Activated abilities MUST contain a colon separating cost and effect
        #    e.g. "{T}: Add {G}" or "Sacrifice a creature: Draw a card"
        if ":" not in effect_text:
            continue

        # 3. Skip lines where the "cost" is empty or whitespace
        left, right = effect_text.split(":", 1)
        if not left.strip():
            continue

        # 4. Skip lines where the cost is ONLY mana symbols without an action
        #    e.g. "{W}{U}{B}{R}{G}" from theme cards
        if re.fullmatch(r"(\s*\{[^}]+\}\s*)+", left.strip()):
            continue

        # ------------------------------------------------------------
        # Parse costs
        # ------------------------------------------------------------
        mana_costs = re.findall(r"\{[^}]+\}", cost_text)
        tap_cost = "{T}" in cost_text

        # Waterbend {X}
        waterbend_cost = None
        m = re.search(r"waterbend\s*\{(\d+)\}", cost_text.lower())
        if m:
            waterbend_cost = int(m.group(1))

        # ------------------------------------------------------------
        # Restrictions
        # ------------------------------------------------------------
        restrictions = []
        if "activate only as a sorcery" in effect_text.lower():
            restrictions.append("activate_only_as_sorcery")

        # ------------------------------------------------------------
        # Permissions
        # ------------------------------------------------------------
        permissions = []
        if "without paying its mana cost" in effect_text.lower():
            permissions.append("free_cast")

        # ------------------------------------------------------------
        # Targeting (activated abilities may target)
        # ------------------------------------------------------------
        targeting = targeting_rules.derive_targeting_from_text(effect_text, game_state)

        # ------------------------------------------------------------
        # Build action
        # ------------------------------------------------------------
        actions.append(
            ActivateAbilityAction(
                allowed=True,
                costs={
                    "mana": mana_costs,
                    "tap": tap_cost,
                    "waterbend": waterbend_cost,
                },
                restrictions=restrictions,
                permissions=permissions,
                effect_text=effect_text,
                targeting_rules=targeting,
                visibility_constraints=VisibilityConstraints(
                    revealed=False,
                    randomized=False,
                ),
                turn_permissions=TurnPermissions(controller_only=True),
            )
        )

    return actions

def _build_special_actions(axis1_card: Axis1Card, game_state: GameState) -> List[SpecialAction]:
    actions: List[SpecialAction] = []
    text = (axis1_card.faces[0].oracle_text or "").lower()

    # ------------------------------------------------------------
    # Morph
    # ------------------------------------------------------------
    if "morph" in text:
        m = re.search(r"morph\s*\{([^}]+)\}", text)
        cost = m.group(1) if m else None
        actions.append(
            SpecialAction(
                kind="morph",
                cost=cost,
                zones=["Hand"],
                effect="Cast face down as a 2/2 creature",
            )
        )

    # ------------------------------------------------------------
    # Foretell
    # ------------------------------------------------------------
    if "foretell" in text:
        m = re.search(r"foretell\s*\{([^}]+)\}", text)
        cost = m.group(1) if m else None
        actions.append(
            SpecialAction(
                kind="foretell",
                cost=cost,
                zones=["Hand"],
                effect="Exile face down; cast later for foretell cost",
            )
        )

    # ------------------------------------------------------------
    # Prototype
    # ------------------------------------------------------------
    if "prototype" in text:
        m = re.search(r"prototype\s*\{([^}]+)\}", text)
        cost = m.group(1) if m else None
        actions.append(
            SpecialAction(
                kind="prototype",
                cost=cost,
                zones=["Hand"],
                effect="Cast as smaller creature with prototype stats",
            )
        )

    # ------------------------------------------------------------
    # Adventure
    # ------------------------------------------------------------
    if "adventure" in text:
        actions.append(
            SpecialAction(
                kind="adventure",
                cost=None,
                zones=["Hand"],
                effect="Cast adventure half of the card",
            )
        )

    return actions


# ------------------------------------------------------------
# PUBLIC BUILDER API
# ------------------------------------------------------------

class Axis2Builder:
    """
    Axis2Builder converts a static Axis1Card + GameState into a fully populated Axis2Card.

    This is the central point where all runtime rules logic is collected.
    """

    @staticmethod
    def build(axis1_card: Axis1Card, game_state: GameState) -> Axis2Card:
        print(f"Building Axis2Card")
        # 1. Actions
        cast_spell_action = _build_cast_spell_action(axis1_card, game_state)
        play_land_action = _build_play_land_action(axis1_card, game_state)
        activate_ability_actions = _build_activate_ability_actions(axis1_card, game_state)
        special_actions = _build_special_actions(axis1_card, game_state)

        actions: Dict[str, Any] = {
            "cast_spell": cast_spell_action,
            "play_land": play_land_action,
            "activate_ability": activate_ability_actions,
            "special_actions": special_actions,
        }

        print(f"Step 1: modal spell parsing")
        # 1b. Modal spell parsing
        mode_choice, modes = modes_rules.parse_modes(axis1_card.faces[0].oracle_text, game_state)

        print(f"Step 2: triggers")
        # 2. Triggers (from oracle text + Axis1 tags)
        triggers: List[Trigger] = effects_rules.derive_triggers(axis1_card, game_state)

        print(f"Step 3: zone permissions")
        # 3. Zone permissions (where you can cast/play from)
        zone_permissions = _derive_zone_permissions(axis1_card, game_state)

        print(f"Step 4: global restrictions")
        # 4. Global restrictions from game state (e.g., Rule of Law)
        global_restrictions = _derive_global_restrictions(game_state)

        print(f"Step 5: general conditions")
        # 5. General conditions attached to this card's actions
        conditions = _derive_conditions(axis1_card)

        print(f"Step 6: choice constraints")
        # 6. Choice constraints (e.g. distinct modes for modal spells)
        choice_constraints = _derive_choice_constraints(axis1_card)

        print(f"Step 7: limits")
        # 7. Limits (per turn, commander tax, spell-per-turn, land-per-turn)
        limits = _derive_limits(axis1_card, game_state)

        print(f"Step 8: visibility constraints")
        # 8. Visibility constraints (face-down, hidden zones, randomization)
        visibility_constraints = _derive_visibility_constraints(axis1_card)

        print(f"Step 9: keywords")
        # 9. Keywords (from oracle text)
        keywords = keywords_rules.derive_keyword_abilities(axis1_card, game_state)
        
        print(f"Step 10: static continuous effects")
        # 10. Static continuous effects on this card (for Axis3 layers)
        static_effects = static_effects_rules.derive_static_effects(axis1_card, game_state)

        print(f"Step 11: replacement/prevention effects")
        # 11. Replacement/prevention effects at the card level
        replacement_effects = replacement_rules.derive_replacement_effects(axis1_card, game_state)

        print(f"Step 12: action replacements, preventions, modifiers")
        # 12. Action replacements, preventions, modifiers (structural hooks)
        action_replacements = _derive_action_replacements(axis1_card, game_state, replacement_effects)
        action_preventions = _derive_action_preventions(axis1_card, game_state, static_effects)
        action_modifiers = _derive_action_modifiers(axis1_card, game_state, static_effects)

        print(f"Step 13: mandatory actions")
        # 13. Mandatory actions (e.g. "must attack if able")
        mandatory_actions = _derive_mandatory_actions(axis1_card, game_state, static_effects)

        print(f"Step 14: ETB replacement effects")
        # 14. ETB replacement effects ("As this enters...", "This enters with...", etc.)
        oracle = axis1_card.faces[0].oracle_text or ""
        etb_effects = etb_replacement_rules.derive_etb_replacement_effects(oracle)
        replacement_effects.extend(etb_effects)

        print(f"Step 15: activated abilities")
        # 15. Activated abilities
        activated_abilities = activated_abilities_rules.derive_activated_abilities(axis1_card)

        print(f"Step 16: returning Axis2Card")
        return Axis2Card(
            actions=actions,
            triggers=triggers,
            zone_permissions=zone_permissions,
            global_restrictions=global_restrictions,
            conditions=conditions,
            action_replacements=action_replacements,
            action_preventions=action_preventions,
            action_modifiers=action_modifiers,
            mandatory_actions=mandatory_actions,
            choice_constraints=choice_constraints,
            limits=limits,
            visibility_constraints=visibility_constraints,
            keywords=keywords,
            static_effects=static_effects,
            replacement_effects=replacement_effects,
            modes=modes,
            mode_choice=mode_choice,
            activated_abilities=activated_abilities,
        )
