import re
from typing import List

from axis1.schema import Axis1Card
from axis2.schema import ContinuousEffect, StaticEffect
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

def _normalize_effect(e):
    # Already a dataclass → OK
    if hasattr(e, "kind"):
        return e

    # Dict → convert to ContinuousEffect
    if isinstance(e, dict):
        return ContinuousEffect(
            kind=e.get("kind") or e.get("type") or "",
            subject=e.get("subject", ""),
            value=e.get("value", {}),
            layering=e.get("layering", "rule_modification"),
        )

    # Unknown → wrap safely
    return ContinuousEffect(
        kind=str(e),
        subject="",
        value={},
        layering="rule_modification",
    )


# ------------------------------------------------------------
# REGEX PATTERNS FOR STATIC EFFECTS
# ------------------------------------------------------------

PT_MOD_PATTERN = re.compile(
    r"(?P<subject>creatures you control|other creatures you control|[a-z ]+ you control)"
    r" get (?P<mod>[+-]\d+/[+-]\d+)",
    re.IGNORECASE,
)

GRANT_ABILITY_PATTERN = re.compile(
    r"(?P<subject>creatures you control|other creatures you control|[a-z ]+ you control)"
    r" have (?P<ability>.+?)(?:\.|\n|$)",
    re.IGNORECASE,
)

# Self ability: "CARDNAME has flying." (we don't know the name, so we key on "has X" lines)
SELF_HAS_ABILITY_PATTERN = re.compile(
    r"\bhas (?P<ability>flying|first strike|double strike|deathtouch|hexproof|indestructible|menace|lifelink|trample|vigilance)\b",
    re.IGNORECASE,
)

COST_INCREASE_PATTERN = re.compile(
    r"spells your opponents cast cost (?P<amount>\{[^}]+\}) more",
    re.IGNORECASE,
)

COST_REDUCTION_PATTERN = re.compile(
    r"spells you cast cost (?P<amount>\{[^}]+\}) less",
    re.IGNORECASE,
)

CANT_GAIN_LIFE_PATTERN = re.compile(
    r"(players|your opponents) can't gain life",
    re.IGNORECASE,
)

CANT_ATTACK_PATTERN = re.compile(
    r"creatures can't attack",
    re.IGNORECASE,
)

CANT_BLOCK_PATTERN = re.compile(
    r"creatures can't block",
    re.IGNORECASE,
)

ETB_TAPPED_PATTERN = re.compile(
    r"(?P<object>this|it|[a-zA-Z0-9 ,'\-]+?) "
    r"enter(?:s)?(?: the battlefield)? tapped",
    re.IGNORECASE,
)

BASE_PT_PATTERN = re.compile(
    r"(?:has|have) base power and toughness (?P<pt>[0-9\*]+/[0-9\*]+)",
    re.IGNORECASE,
)

PT_EQUAL_PATTERN = re.compile(
    r"power and toughness are each equal to (?P<formula>.+?)(?:\.|\n|$)",
    re.IGNORECASE,
)

TYPE_CHANGE_PATTERN = re.compile(
    r"(?P<subject>[a-z ]+ you control|[a-z ]+)\s+are\s+(?P<types>[a-z ,]+)(?: in addition to their other types)?",
    re.IGNORECASE,
)

TYPE_ADD_IN_ADDITION_PATTERN = re.compile(
    r"(?P<subject>[a-z ]+ you control|[a-z ]+)\s+are\s+(?P<types>[a-z ,]+)\s+in addition to their other types",
    re.IGNORECASE,
)

COLOR_CHANGE_PATTERN = re.compile(
    r"(?P<subject>creatures you control|other creatures you control|[a-z ]+)\s+are\s+(?P<colors>white|blue|black|red|green|colorless)",
    re.IGNORECASE,
)

SELF_COLOR_PATTERN = re.compile(
    r"is (white|blue|black|red|green|colorless)",
    re.IGNORECASE,
)

LOSE_ABILITY_PATTERN = re.compile(
    r"(?P<subject>creatures your opponents control|creatures you control|enchanted creature|[a-z ]+)\s+lose(?:s)? (?P<ability>flying|first strike|double strike|deathtouch|hexproof|indestructible|menace|lifelink|trample|vigilance|all abilities)",
    re.IGNORECASE,
)

ATTACK_EACH_COMBAT_PATTERN = re.compile(
    r"(?P<subject>creatures you control|creatures your opponents control|creatures)\s+attack each combat if able",
    re.IGNORECASE,
)

BLOCK_EACH_COMBAT_PATTERN = re.compile(
    r"(?P<subject>creatures you control|creatures your opponents control|creatures)\s+block each combat if able",
    re.IGNORECASE,
)

ONE_SPELL_PER_TURN_PATTERN = re.compile(
    r"players can(?: only)? cast (?:one|a single) spell each turn",
    re.IGNORECASE,
)

SORCERY_SPEED_CAST_PATTERN = re.compile(
    r"can cast spells only any time they could cast a sorcery",
    re.IGNORECASE,
)

PREVENT_DAMAGE_PATTERN = re.compile(
    r"prevent all (combat )?damage that would be dealt to (?P<subject>creatures you control|you|[a-z ]+)",
    re.IGNORECASE,
)

YOU_MAY_LOOK_AT_PATTERN = re.compile(
    r"you may look at the top card of your library any time",
    re.IGNORECASE,
)

PLAY_FROM_GRAVEYARD_PATTERN = re.compile(
    r"you may play lands? from your graveyard",
    re.IGNORECASE,
)


# ------------------------------------------------------------
# MAIN STATIC EFFECT PARSER
# ------------------------------------------------------------

def derive_static_effects(axis1_card: Axis1Card, game_state: "GameState") -> List[ContinuousEffect]:
    """
    Extract continuous static effects from oracle text.
    Produces structured ContinuousEffect objects for Axis3 layer system.
    """

    text = _oracle_text(axis1_card)
    effects: List[ContinuousEffect] = []

    # ------------------------------------------------------------
    # P/T Modifiers (Layer 7c)
    # ------------------------------------------------------------
    for m in PT_MOD_PATTERN.finditer(text):
        p, t = m.group("mod").split("/")
        effects.append(
            ContinuousEffect(
                kind="pt_modifier",
                subject=m.group("subject"),
                value={"power": int(p), "toughness": int(t)},
                layering="layer_7c",
            )
        )

    # Base P/T setters (Layer 7b)
    for m in BASE_PT_PATTERN.finditer(text):
        pt = m.group("pt")
        p, t = pt.split("/")
        effects.append(
            ContinuousEffect(
                kind="base_pt_set",
                subject="enchanted_or_affected",
                value={"power": p, "toughness": t},
                layering="layer_7b",
            )
        )

    for m in PT_EQUAL_PATTERN.finditer(text):
        effects.append(
            ContinuousEffect(
                kind="base_pt_formula",
                subject="self",
                value={"formula": m.group("formula").strip()},
                layering="layer_7b",
            )
        )

    # ------------------------------------------------------------
    # Ability Grants (Layer 6)
    # ------------------------------------------------------------
    for m in GRANT_ABILITY_PATTERN.finditer(text):
        effects.append(
            ContinuousEffect(
                kind="grant_ability",
                subject=m.group("subject"),
                value={"ability": m.group("ability").strip()},
                layering="layer_6",
            )
        )

    # Self static abilities: "has flying", etc.
    for m in SELF_HAS_ABILITY_PATTERN.finditer(text):
        effects.append(
            ContinuousEffect(
                kind="grant_ability",
                subject="self",
                value={"ability": m.group("ability").strip()},
                layering="layer_6",
            )
        )

    # Ability removal
    for m in LOSE_ABILITY_PATTERN.finditer(text):
        ability = m.group("ability").strip()
        subject = m.group("subject").strip()
        effects.append(
            ContinuousEffect(
                kind="lose_ability",
                subject=subject,
                value={"ability": ability},
                layering="layer_6",
            )
        )

    # ------------------------------------------------------------
    # Cost Modifiers (Layer 7a)
    # ------------------------------------------------------------
    if m := COST_INCREASE_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="cost_increase",
                subject="opponent_spells",
                value={"amount": m.group("amount")},
                layering="layer_7a",
            )
        )

    if m := COST_REDUCTION_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="cost_reduction",
                subject="your_spells",
                value={"amount": m.group("amount")},
                layering="layer_7a",
            )
        )

    # ------------------------------------------------------------
    # Type-changing (Layer 4)
    # ------------------------------------------------------------
    for m in TYPE_ADD_IN_ADDITION_PATTERN.finditer(text):
        subject = m.group("subject").strip()
        types = [t.strip() for t in m.group("types").split(",")]
        effects.append(
            ContinuousEffect(
                kind="add_types",
                subject=subject,
                value={"types": types},
                layering="layer_4",
            )
        )

    for m in TYPE_CHANGE_PATTERN.finditer(text):
        subject = m.group("subject").strip()
        types = [t.strip() for t in m.group("types").split(",")]
        effects.append(
            ContinuousEffect(
                kind="set_types",
                subject=subject,
                value={"types": types},
                layering="layer_4",
            )
        )

    # ------------------------------------------------------------
    # Color-changing (Layer 5)
    # ------------------------------------------------------------
    for m in COLOR_CHANGE_PATTERN.finditer(text):
        subject = m.group("subject").strip()
        color = m.group("colors").strip()
        effects.append(
            ContinuousEffect(
                kind="set_color",
                subject=subject,
                value={"color": color},
                layering="layer_5",
            )
        )

    if m := SELF_COLOR_PATTERN.search(text):
        color = m.group(1).strip()
        effects.append(
            ContinuousEffect(
                kind="set_color",
                subject="self",
                value={"color": color},
                layering="layer_5",
            )
        )

    # ------------------------------------------------------------
    # Rule Modifications
    # ------------------------------------------------------------
    if CANT_GAIN_LIFE_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="cant_gain_life",
                subject="players",
                value={},
                layering="rule_modification",
            )
        )

    if CANT_ATTACK_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="cant_attack",
                subject="creatures",
                value={},
                layering="rule_modification",
            )
        )

    if CANT_BLOCK_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="cant_block",
                subject="creatures",
                value={},
                layering="rule_modification",
            )
        )

    if ONE_SPELL_PER_TURN_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="one_spell_per_turn",
                subject="players",
                value={},
                layering="rule_modification",
            )
        )

    if SORCERY_SPEED_CAST_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="cast_only_sorcery_speed",
                subject="players",
                value={},
                layering="rule_modification",
            )
        )

    # ------------------------------------------------------------
    # Combat rule modifications
    # ------------------------------------------------------------
    for m in ATTACK_EACH_COMBAT_PATTERN.finditer(text):
        subject = m.group("subject").strip()
        effects.append(
            ContinuousEffect(
                kind="attack_each_combat_if_able",
                subject=subject,
                value={},
                layering="rule_modification",
            )
        )

    for m in BLOCK_EACH_COMBAT_PATTERN.finditer(text):
        subject = m.group("subject").strip()
        effects.append(
            ContinuousEffect(
                kind="block_each_combat_if_able",
                subject=subject,
                value={},
                layering="rule_modification",
            )
        )

    # ------------------------------------------------------------
    # Damage prevention
    # ------------------------------------------------------------
    for m in PREVENT_DAMAGE_PATTERN.finditer(text):
        subject = m.group("subject").strip()
        is_combat = "combat " in m.group(0)
        effects.append(
            ContinuousEffect(
                kind="prevent_damage",
                subject=subject,
                value={"combat_only": is_combat},
                layering="replacement",
            )
        )

    # ------------------------------------------------------------
    # Zone / visibility static effects
    # ------------------------------------------------------------
    if YOU_MAY_LOOK_AT_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="may_look_top_library",
                subject="controller",
                value={},
                layering="rule_modification",
            )
        )

    if PLAY_FROM_GRAVEYARD_PATTERN.search(text):
        effects.append(
            ContinuousEffect(
                kind="play_lands_from_graveyard",
                subject="controller",
                value={},
                layering="rule_modification",
            )
        )

    # ------------------------------------------------------------
    # ETB tapped (replacement‑like)
    # ------------------------------------------------------------
    for m in ETB_TAPPED_PATTERN.finditer(text):
        subject = m.group(1).strip()
        effects.append(
            ContinuousEffect(
                kind="enter_tapped",
                subject=subject,
                value={},
                layering="replacement",
            )
        )

    # ------------------------------------------------------------
    # Add global continuous effects from game state
    # ------------------------------------------------------------
    for effect in game_state.continuous_effects:
        effects.append(effect)

    face = axis1_card.faces[0] 
    axis1_static = getattr(face, "static_effects", []) 
    # Add static effects from axis1_card
    for eff in axis1_static:
        if eff["kind"] == "type_changer":
            effects.append(
                StaticEffect(
                    kind="type_changer",
                    subject="this",                     # Axis1 always outputs subject="this" for now
                    value={
                        "types": eff["value"]["types"], # e.g. ["all_creature_types"]
                        "add": eff["value"].get("add", True),
                        "remove": eff["value"].get("remove", False),
                    },
                    layering=eff["layering"],           # always "layer_4" for type changes
                    zones=eff.get("zones", ["battlefield"]),
                )
            )

    # Deduplicate
    unique = []
    seen = set()

    for raw in effects:
        e = _normalize_effect(raw)
        key = (e.kind, e.subject, str(e.value))
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique

