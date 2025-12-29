import re
from axis2.rules.keywords import KEYWORD_TRIGGER_MAP
from typing import List

from axis1.schema import Axis1Card
from axis2.schema import Trigger, TargetingRules
from axis2.schema import ReplacementEffect
from typing import TYPE_CHECKING
if TYPE_CHECKING: 
    from axis2.builder import GameState


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _oracle_text(axis1_card: Axis1Card) -> str:
    face = axis1_card.faces[0]
    return (face.oracle_text or "").strip().lower()


def _regex(text: str, pattern: str):
    return re.search(pattern, text, re.IGNORECASE)


# ------------------------------------------------------------
# TRIGGER PARSING
# ------------------------------------------------------------
ETB_PATTERN = re.compile(
    r"when\s+(?:this creature|this permanent|[a-zA-Z0-9\s']+)\s+enters the battlefield[, ]*(.*)",
    flags=re.IGNORECASE
)

def _parse_etb_triggers(text: str) -> List[Trigger]:
    triggers = []

    match = ETB_PATTERN.search(text)
    if not match:
        return triggers

    effect_text = match.group(1).strip()

    # Remove anthem/static text if present
    effect_text = re.split(
        r"creatures you control get",
        effect_text,
        maxsplit=1,
        flags=re.IGNORECASE
    )[0].strip()

    mandatory = " may " not in effect_text.lower()

    if effect_text:
        triggers.append(
            Trigger(
                event="enters_battlefield",
                condition="When this creature enters the battlefield",
                effect_text=effect_text,
                mandatory=mandatory,
            )
        )

    return triggers



def _parse_ltb_triggers(text: str) -> List[Trigger]:
    """
    Detect LTB triggers:
      - "When CARDNAME dies..."
      - "Whenever CARDNAME dies..."
    """

    triggers = []

    if "dies" in text:
        if "when" in text or "whenever" in text:
            triggers.append(
                Trigger(
                    event="dies",
                    condition=None,
                    effect_text=text,
                    mandatory=True
                )
            )

    return triggers


def _parse_attack_triggers(text: str) -> List[Trigger]:
    """
    Detect attack triggers:
      - "Whenever CARDNAME attacks..."
      - "When CARDNAME attacks..."
    """

    triggers = []

    if "attacks" in text:
        if "when" in text or "whenever" in text:
            triggers.append(
                Trigger(
                    event="attacks",
                    condition=None,
                    effect_text=text,
                    mandatory=True
                )
            )

    return triggers


def _parse_block_triggers(text: str) -> List[Trigger]:
    """
    Detect block triggers:
      - "Whenever CARDNAME blocks..."
    """

    triggers = []

    if "blocks" in text:
        if "when" in text or "whenever" in text:
            triggers.append(
                Trigger(
                    event="blocks",
                    condition=None,
                    effect_text=text,
                    mandatory=True
                )
            )

    return triggers


def _parse_upkeep_triggers(text: str) -> List[Trigger]:
    """
    Detect upkeep triggers:
      - "At the beginning of your upkeep..."
      - "At the beginning of each upkeep..."
    """

    triggers = []

    if "at the beginning of" in text and "upkeep" in text:
        triggers.append(
            Trigger(
                event="upkeep",
                condition=None,
                effect_text=text,
                mandatory=True
            )
        )

    return triggers
    
def _extract_keyword_triggered_abilities(axis1_card: Axis1Card) -> List[Trigger]:
    text = (axis1_card.faces[0].oracle_text or "").lower()
    triggers = []

    for kw, data in KEYWORD_TRIGGER_MAP.items():
        if kw in text:
            triggers.append(
                Trigger(
                    event=data["event"],
                    condition=data["condition"],
                    effect_text=data["effect_template"],
                    mandatory=False,
                )
            )

    return triggers




def _parse_draw_step_triggers(text: str) -> List[Trigger]:
    """
    Detect draw step triggers:
      - "At the beginning of your draw step..."
    """

    triggers = []

    if "at the beginning of" in text and "draw step" in text:
        triggers.append(
            Trigger(
                event="draw_step",
                condition=None,
                effect_text=text,
                mandatory=True
            )
        )

    return triggers


def _parse_end_step_triggers(text: str) -> List[Trigger]:
    """
    Detect end step triggers:
      - "At the beginning of your end step..."
    """

    triggers = []

    if "at the beginning of" in text and "end step" in text:
        triggers.append(
            Trigger(
                event="end_step",
                condition=None,
                effect_text=text,
                mandatory=True
            )
        )

        # NEW: "At the beginning of each player's end step" 
        m = re.search( 
            r"at the beginning of each player's end step[, ]*(.*)", 
            text, 
            re.IGNORECASE 
        ) 
        if m: 
            effect = m.group(1).strip() 
            triggers.append( 
                Trigger( 
                    event="end_step",
                    condition="At the beginning of each player's end step", 
                    effect_text=effect, 
                    mandatory=(" may " not in effect.lower()), 
                ) 
            ) 
            return triggers

    return triggers


# ------------------------------------------------------------
# REPLACEMENT EFFECTS
# ------------------------------------------------------------

def _parse_replacement_effects(text: str) -> List[str]:
    """
    Detect replacement effects:
      - "If CARDNAME would die, exile it instead."
      - "If a creature would enter the battlefield under your control, it enters tapped."
      - "If you would draw a card, draw two instead."
    """

    effects = []

    # Dies → exile instead
    if _regex(text, r"if .* would die.* exile .* instead"):
        effects.append("dies_exile_instead")

    # ETB tapped
    if _regex(text, r"enters the battlefield tapped"):
        effects.append("enter_tapped")

    # Draw replacement
    if _regex(text, r"if .* would draw .* draw .* instead"):
        effects.append("draw_replacement")

    # Damage replacement
    if _regex(text, r"if .* would deal damage"):
        effects.append("damage_replacement")

    return effects


# ------------------------------------------------------------
# STATIC EFFECTS (continuous)
# ------------------------------------------------------------

def _parse_static_effects(text: str) -> List[str]:
    """
    Detect static continuous effects related to cost modification, P/T modifiers,
    and other common patterns. Produces structured identifiers that Axis3 can interpret.
    """

    effects = []

    # ------------------------------------------------------------
    # 1. Color-based cost reductions
    # ------------------------------------------------------------
    m = re.search(r"(white|blue|black|red|green) spells you cast cost (\{[^\}]+\}) less", text)
    if m:
        color = m.group(1)
        amount = m.group(2)
        effects.append(f"cost_reduction_color_{color}_{amount}")

    # ------------------------------------------------------------
    # 2. Type-based cost reductions
    # ------------------------------------------------------------
    m = re.search(r"(creature|artifact|enchantment|planeswalker|instant|sorcery) spells you cast cost (\{[^\}]+\}) less", text)
    if m:
        stype = m.group(1)
        amount = m.group(2)
        effects.append(f"cost_reduction_type_{stype}_{amount}")

    # ------------------------------------------------------------
    # 3. Multi-type reductions
    # ------------------------------------------------------------
    m = re.search(r"(instant) and (sorcery) spells you cast cost (\{[^\}]+\}) less", text)
    if m:
        t1, t2, amount = m.group(1), m.group(2), m.group(3)
        effects.append(f"cost_reduction_types_{t1}_{t2}_{amount}")

    # ------------------------------------------------------------
    # 4. Tribal cost reductions
    # ------------------------------------------------------------
    m = re.search(r"([a-zA-Z]+) spells you cast cost (\{[^\}]+\}) less", text)
    if m:
        tribe = m.group(1)
        amount = m.group(2)
        if tribe not in ["creature", "artifact", "instant", "sorcery", "enchantment", "planeswalker"]:
            effects.append(f"cost_reduction_tribal_{tribe}_{amount}")

    # ------------------------------------------------------------
    # 5. Opponent cost increases
    # ------------------------------------------------------------
    m = re.search(r"spells your opponents cast cost (\{[^\}]+\}) more", text)
    if m:
        amount = m.group(1)
        effects.append(f"opponent_spells_cost_more_{amount}")

    # ------------------------------------------------------------
    # 6. Global cost modifiers
    # ------------------------------------------------------------
    m = re.search(r"all spells cost (\{[^\}]+\}) less", text)
    if m:
        amount = m.group(1)
        effects.append(f"global_cost_reduction_{amount}")

    # ------------------------------------------------------------
    # 7. Buffs to your creatures
    #    "Creatures you control get +X/+Y."
    #    "Other creatures you control get +X/+Y."
    # ------------------------------------------------------------
    m = re.search(r"(other )?creatures you control get \+(\d+)/\+(\d+)", text)
    if m:
        prefix = "other_" if m.group(1) else ""
        power = int(m.group(2))
        toughness = int(m.group(3))
        effects.append(f"pt_modifier_{prefix}creatures_you_control_{power}_{toughness}")

    # ------------------------------------------------------------
    # 8. Debuffs to opponent creatures
    #    "Creatures your opponents control get -X/-Y."
    # ------------------------------------------------------------
    m = re.search(r"creatures your opponents control get -(\d+)/-(\d+)", text)
    if m:
        power = -int(m.group(1))
        toughness = -int(m.group(2))
        effects.append(f"pt_modifier_creatures_opponents_control_{power}_{toughness}")

    # ------------------------------------------------------------
    # 9. Life gain prevention
    # ------------------------------------------------------------
    if "your opponents can't gain life" in text:
        effects.append("opponents_cannot_gain_life")

    if "players can't gain life" in text:
        effects.append("players_cannot_gain_life")

    return effects

# ------------------------------------------------------------
# MAIN EFFECT DERIVATION
# ------------------------------------------------------------

def derive_triggers(axis1_card: Axis1Card, game_state: "GameState") -> List[Trigger]:
    triggers: List[Trigger] = []

    text = _oracle_text(axis1_card)
    face = axis1_card.faces[0]

    # Axis1 triggers (structured)
    axis1_triggers = list(getattr(face, "triggered_abilities", []))

    if axis1_triggers:
        # Use Axis1 triggers only
        for trig in axis1_triggers:
            condition = trig.condition
            effect = trig.effect
            event_hint = trig.event_hint

            mandatory = " may " not in condition.lower()

            trigger = Trigger(
                event=event_hint,
                condition=condition,
                effect_text=effect,
                mandatory=mandatory,
            )

            # Targeting detection (your existing logic)
            m = re.search(r"target\s+(creature|player|creature or player|any target)", effect, re.IGNORECASE)
            if m:
                target_type = m.group(1).lower()
                if target_type == "creature or player":
                    legal = ["creature", "player"]
                elif target_type == "any target":
                    legal = ["any"]
                else:
                    legal = [target_type]

                trigger.targeting_rules = TargetingRules(
                    required=True,
                    min=1,
                    max=1,
                    legal_targets=legal,
                    restrictions=[],
                    replacement_effects=[]
                )

            triggers.append(trigger)

    else:
        # Fallback: raw-text parsing
        triggers.extend(_parse_etb_triggers(text))
        triggers.extend(_parse_ltb_triggers(text))
        triggers.extend(_parse_attack_triggers(text))
        triggers.extend(_parse_block_triggers(text))
        triggers.extend(_parse_upkeep_triggers(text))
        triggers.extend(_parse_draw_step_triggers(text))
        triggers.extend(_parse_end_step_triggers(text))

    # Keyword-trigger abilities (exploit, mentor, etc.)
    triggers.extend(_extract_keyword_triggered_abilities(axis1_card))

    # Deduplicate by event + effect_text
    unique = []
    seen = set()

    for t in triggers:
        key = (t.event, t.effect_text.strip().lower())
        if key not in seen:
            seen.add(key)
            unique.append(t)

    return unique



def derive_replacement_effects(axis1_card: Axis1Card, game_state: "GameState") -> List[ReplacementEffect]:
    """
    Extract replacement effects from oracle text.
    """

    text = _oracle_text(axis1_card)
    effects = _parse_replacement_effects(text)

    # Add global replacement effects from game state
    for effect in game_state.replacement_effects:
        if isinstance(effect, str):
            effects.append(effect)
        else:
            kind = effect.get("type")
            if kind:
                effects.append(kind)

    # Deduplicate
    return list(dict.fromkeys(effects))


def derive_static_effects(axis1_card: Axis1Card, game_state: "GameState") -> List[str]:
    """
    Extract static continuous effects from oracle text.
    """

    text = _oracle_text(axis1_card)
    effects = _parse_static_effects(text)

    # Add continuous effects from game state
    for effect in game_state.continuous_effects:
        etype = effect.get("type")
        if etype:
            effects.append(etype)

    return list(dict.fromkeys(effects))
