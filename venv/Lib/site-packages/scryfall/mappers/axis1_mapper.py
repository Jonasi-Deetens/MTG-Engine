import re
import unicodedata
from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics, Axis1Metadata, Axis1ActivatedAbility, Axis1TriggeredAbility

# ------------------------------------------------------------
# Activated ability parsing from oracle text
# ------------------------------------------------------------

# Matches "COST: EFFECT"
# Example:
#   "{T}: Add {U}."
#   "{2}{W}{U}, {T}, Sacrifice this land: Draw a card."

ACTIVATED_ABILITY_LINE_RE = re.compile(
    r"^\s*(?P<costs>[^:]+?)\s*:\s*(?P<effect>.+)$"
)

PLANESWALKER_ABILITY_RE = re.compile(
    r"^\s*(?P<loyalty>[+\-]?\d+)\s*:\s*(?P<effect>.+)$"
)

MANA_SYMBOL_RE = re.compile(r"\{[^}]+\}")

def _extract_static_type_changers(oracle_text: str):
    """
    Detect static abilities that change types in all zones or on the battlefield.
    Produces Axis1-style static effect dicts that map cleanly into the Axis2 StaticEffect schema.
    """
    if not oracle_text:
        return []

    t = oracle_text.lower()
    effects = []

    # ------------------------------------------------------------
    # Mistform Ultimus / Changeling / "is every creature type"
    # Applies in ALL ZONES
    # ------------------------------------------------------------
    if (
        "every creature type" in t
        or "all creature types" in t
        or "each creature type" in t
        or "changeling" in t
    ):
        effects.append({
            "kind": "type_changer",
            "subject": "this",
            "value": {
                "types": ["all_creature_types"],
                "add": True,
                "remove": False,
            },
            "layering": "layer_4",
            "zones": ["all"],
        })

    # ------------------------------------------------------------
    # Maskwood Nexus / Arcane Adaptation / Conspiracy
    # "is all types" / "are all types"
    # Applies on the battlefield only
    # ------------------------------------------------------------
    if (
        "is every type" in t
        or "is all types" in t
        or "are all types" in t
    ):
        effects.append({
            "kind": "type_changer",
            "subject": "this",
            "value": {
                "types": ["all_types"],
                "add": True,
                "remove": False,
            },
            "layering": "layer_4",
            "zones": ["battlefield"],
        })

    return effects


def _extract_activation_conditions(effect_text: str) -> list:
    """
    Pull out common activation condition clauses from the effect text.
    This is *optional metadata* Axis2/Axis3 can use later.
    """
    t = effect_text.lower()
    conditions = []

    if "activate only as a sorcery" in t:
        conditions.append({"type": "timing", "value": "sorcery_only"})
    if "activate only once each turn" in t:
        conditions.append({"type": "limit_per_turn", "value": 1})
    if "activate only during your turn" in t:
        conditions.append({"type": "timing", "value": "your_turn_only"})
    if "activate only during combat" in t:
        conditions.append({"type": "timing", "value": "combat_only"})
    if "activate only before blockers are declared" in t:
        conditions.append({"type": "timing", "value": "before_blockers"})
    if "activate only if you control" in t:
        conditions.append({"type": "board_condition", "value": "requires_controlled_perm"})
    if "activate only if an opponent controls" in t:
        conditions.append({"type": "board_condition", "value": "requires_opponent_control"})

    return conditions


def _parse_cost_metadata(cost_text: str) -> dict:
    """
    Derive some helpful boolean flags from the cost string.
    This is purely descriptive, Axis2 can choose to use or ignore it.
    """
    lower = cost_text.lower()

    tap = "{t}" in lower or "{T}" in cost_text
    sacrifice_self = "sacrifice" in lower and ("this" in lower or "land" in lower or "creature" in lower)
    discard_this = "discard" in lower and "this card" in lower

    # Extract mana symbols in the cost portion
    mana_symbols = MANA_SYMBOL_RE.findall(cost_text)
    # Filter out tap symbol
    mana_symbols = [m for m in mana_symbols if m.upper() != "{T}"]

    return {
        "tap": tap,
        "sacrifice_self": sacrifice_self,
        "discard_self": discard_this,
        "mana_cost_symbols": mana_symbols,
    }


def _extract_activated_abilities_from_oracle(oracle_text: str) -> list:
    if not oracle_text:
        return []

    abilities = []

    for raw_line in oracle_text.split("\n"):
        line = raw_line.strip()
        # Normalize Unicode punctuation and whitespace
        line = (
            line.replace("：", ":")      # fullwidth colon → ASCII colon
                .replace("\u2028", " ") # line separator → space
                .replace("\u00A0", " ") # non-breaking space → space
                .replace("\u200B", "")  # zero-width space → remove
        )

        if not line:
            continue

        # Skip reminder text
        if line.startswith("(") and line.endswith(")"):
            inner = line[1:-1].strip()
            line = inner

        # ------------------------------------------------------------
        # 1. Planeswalker loyalty abilities
        # ------------------------------------------------------------
        m = PLANESWALKER_ABILITY_RE.match(line)
        if m:
            loyalty_raw = m.group("loyalty").strip()
            effect_text = m.group("effect").strip()

            # Normalize unicode minus
            loyalty_cost = int(loyalty_raw.replace("−", "-"))

            ability = Axis1ActivatedAbility(
                raw=line,
                cost=loyalty_raw,
                effect=effect_text,
                cost_metadata={"loyalty": loyalty_cost},
                activation_conditions=[],
            )
            abilities.append(ability)
            continue

        m = re.match(r"equip\s+(?P<cost>\{[^}]+\})", line, re.IGNORECASE)
        if m:
            cost_text = m.group("cost")
            abilities.append(
                Axis1ActivatedAbility(
                    raw=line,
                    cost=cost_text,
                    effect="Attach this to target creature you control.",
                    cost_metadata=_parse_cost_metadata(cost_text),
                    activation_conditions=["sorcery_speed"],
                )
            )
            continue

        # ------------------------------------------------------------
        # 2. Normal activated abilities
        # ------------------------------------------------------------
        m = ACTIVATED_ABILITY_LINE_RE.match(line)
        if not m:
            continue

        cost_text = m.group("costs").strip()
        effect_text = m.group("effect").strip()

        # Split multiple costs: "{T}, Sacrifice this land"
        cost_parts = [c.strip() for c in cost_text.split(",")]

        parsed_costs = []
        for part in cost_parts:
            parsed_costs.append({
                "raw": part,
                "metadata": _parse_cost_metadata(part)
            })

        ability = Axis1ActivatedAbility(
            raw=line,
            cost=cost_text,
            cost_parts=parsed_costs,
            effect=effect_text,
            cost_metadata={},
            activation_conditions=_extract_activation_conditions(effect_text),
        )
        abilities.append(ability)

    return abilities


# ------------------------------------------------------------
# Triggered ability parsing from oracle text
# ------------------------------------------------------------

TRIGGER_STARTERS = (
    "whenever ",
    "when ",
    "at the beginning of ",
    "at the end of ",
    "at the beginning of your ",
    "at the beginning of each ",
    "at the beginning of combat ",
)

def _extract_event_hint(trigger_condition: str) -> str:
    """
    Convert a trigger condition into a normalized event hint.
    This helps Axis2/Axis3 match game events.
    """

    t = trigger_condition.lower()

    # Combat damage triggers
    if "deals combat damage to a player" in t:
        return "deals_combat_damage_to_player"
    if "deals combat damage to a creature" in t:
        return "deals_combat_damage_to_creature"

    # ETB
    if "enters the battlefield" in t:
        return "enters_battlefield"

    # Dies
    if "dies" in t:
        return "dies"

    # Cast triggers
    if "cast" in t:
        return "spell_cast"

    # Attack triggers
    if "attacks" in t:
        return "attacks"

    # Upkeep
    if "at the beginning of your upkeep" in t:
        return "upkeep"

    # Draw step
    if "at the beginning of your draw step" in t:
        return "draw_step"

    # End step
    if "at the beginning of your end step" in t:
        return "end_step"# Transform triggers

    if "transforms into" in t:
        return "transform"

    # ETB triggers with "enters" but not "enters the battlefield"
    if "enters" in t:
        return "enters_battlefield"

    # Upkeep triggers (each upkeep)
    if "at the beginning of each upkeep" in t:
        return "upkeep"

    # Fallback
    return "generic_trigger"


def _extract_triggered_abilities_from_oracle(oracle_text: str) -> list:
    """
    Parse triggered abilities from oracle text.
    Trigger lines start with:
        - "Whenever ..."
        - "When ..."
        - "At the beginning of ..."
    """

    if not oracle_text:
        return []

    abilities = []
    lines = oracle_text.split("\n")

    for raw_line in lines:
        line = raw_line.strip()
        # Normalize Unicode punctuation and whitespace
        line = (
            line.replace("：", ":")      # fullwidth colon → ASCII colon
                .replace("\u2028", " ") # line separator → space
                .replace("\u00A0", " ") # non-breaking space → space
                .replace("\u200B", "")  # zero-width space → remove
        )

        if not line:
            continue

        lower = line.lower()

        # Check if this line starts a triggered ability
        if not any(lower.startswith(prefix) for prefix in TRIGGER_STARTERS): 
            continue

        # Split into condition + effect
        # Example:
        #   "Whenever this creature deals combat damage to a player, that player reveals their hand."
        if "," in line:
            condition, effect = line.split(",", 1)
            condition = condition.strip()
            effect = effect.strip()
        else:
            # Rare case: no comma
            condition = line
            effect = ""

        event_hint = _extract_event_hint(condition)
        ability = Axis1TriggeredAbility(
            raw=line,
            condition=condition,
            effect=effect,
            event_hint=event_hint,
        )
        abilities.append(ability)

    return abilities

class Axis1Mapper:
    def map(self, scry: dict) -> Axis1Card:

        # ------------------------------------------------------------
        # 1. Handle multi-face cards (modal_dfc, transform, split, adventure)
        # ------------------------------------------------------------
        faces = []
        if "card_faces" in scry and scry["card_faces"]:
            for idx, f in enumerate(scry["card_faces"]):
                type_line = f.get("type_line", "")
                if "—" in type_line:
                    types_part, subtypes_part = [p.strip() for p in type_line.split("—", 1)]
                    card_types = types_part.split()
                    subtypes = subtypes_part.split()
                else:
                    card_types = type_line.split()
                    subtypes = []

                oracle_text = f.get("oracle_text")

                face = Axis1Face(
                    face_id=f"face_{idx}",
                    name=f.get("name"),
                    mana_cost=f.get("mana_cost"),
                    mana_value=f.get("cmc", scry.get("cmc")),
                    colors=f.get("colors", []),
                    color_indicator=f.get("color_indicator") or [],
                    card_types=card_types,
                    supertypes=[t for t in card_types if t in ["Legendary", "Basic", "Snow", "World", "Ongoing"]],
                    subtypes=subtypes,
                    power=f.get("power"),
                    toughness=f.get("toughness"),
                    loyalty=f.get("loyalty"),
                    defense=f.get("defense"),
                    oracle_text=oracle_text,
                    keywords=f.get("keywords", []),
                    activated_abilities=_extract_activated_abilities_from_oracle(oracle_text or ""),
                    triggered_abilities=_extract_triggered_abilities_from_oracle(oracle_text or ""),
                    static_effects=_extract_static_type_changers(oracle_text or ""),
                )
                faces.append(face)

            # Use the *front face* for characteristics
            front = faces[0]
            card_types = front.card_types
            subtypes = front.subtypes

        else:
            # ------------------------------------------------------------
            # 2. Normal single-face card
            # ------------------------------------------------------------
            type_line = scry.get("type_line", "")
            if "—" in type_line:
                types_part, subtypes_part = [p.strip() for p in type_line.split("—", 1)]
                card_types = types_part.split()
                subtypes = subtypes_part.split()
            else:
                card_types = type_line.split()
                subtypes = []

            oracle_text = scry.get("oracle_text")

            face = Axis1Face(
                face_id="front",
                name=scry["name"],
                mana_cost=scry.get("mana_cost"),
                mana_value=scry.get("cmc"),
                colors=scry.get("colors", []),
                color_indicator=scry.get("color_indicator") or [],
                card_types=card_types,
                supertypes=[t for t in card_types if t in ["Legendary", "Basic", "Snow", "World", "Ongoing"]],
                subtypes=subtypes,
                power=scry.get("power"),
                toughness=scry.get("toughness"),
                loyalty=scry.get("loyalty"),
                defense=scry.get("defense"),
                oracle_text=oracle_text,
                keywords=scry.get("keywords", []),
                activated_abilities=_extract_activated_abilities_from_oracle(oracle_text or ""),
                triggered_abilities=_extract_triggered_abilities_from_oracle(oracle_text or ""),
                static_effects=_extract_static_type_changers(oracle_text or ""),
            )
            faces = [face]

        # ------------------------------------------------------------
        # 3. Characteristics (based on front face)
        # ------------------------------------------------------------
        characteristics = Axis1Characteristics(
            mana_cost=faces[0].mana_cost,
            mana_value=faces[0].mana_value,
            colors=faces[0].colors,
            color_identity=scry.get("color_identity", []),
            color_indicator=faces[0].color_indicator,
            card_types=faces[0].card_types,
            supertypes=faces[0].supertypes,
            subtypes=faces[0].subtypes,
            power=faces[0].power,
            toughness=faces[0].toughness,
            loyalty=faces[0].loyalty,
            defense=faces[0].defense,
        )

        # ------------------------------------------------------------
        # 4. Metadata
        # ------------------------------------------------------------
        metadata = Axis1Metadata(
            rarity=scry.get("rarity"),
            artist=scry.get("artist"),
            illustration_id=scry.get("illustration_id"),
            frame=scry.get("frame"),
            border_color=scry.get("border_color"),
            watermark=scry.get("watermark"),
            legalities=scry.get("legalities") or {},
            image_uris=scry.get("image_uris") or {},
        )

        # ------------------------------------------------------------
        # 5. Build Axis1Card
        # ------------------------------------------------------------
        axis1 = Axis1Card(
            card_id=scry["id"],
            oracle_id=scry.get("oracle_id"),
            scryfall_id=scry.get("id"),
            set=scry.get("set"),
            collector_number=scry.get("collector_number"),
            lang=scry.get("lang"),
            layout=scry.get("layout", "normal"),
            object_kind="card",
            names=[f.name for f in faces],
            printed_name=scry.get("printed_name", faces[0].name),
            faces=faces,
            characteristics=characteristics,
            intrinsic_rules=[],
            intrinsic_limits=[],
            intrinsic_counters=[],
            characteristic_sources={},
            rules_tags=[],
            metadata=metadata,
        )

        return axis1
