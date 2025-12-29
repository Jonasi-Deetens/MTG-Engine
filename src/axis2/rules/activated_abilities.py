import re

from axis3.translate.ability_parsing.costs import parse_cost_string
from axis3.translate.ability_parsing.effects import parse_effect_string
from axis2.schema import ActivatedAbility
from axis1.schema import Axis1Card

ACTIVATED_ABILITY_PATTERN = re.compile(
    r"""^
    (?P<cost>
        (?:\{[^}]+\})+                     # one or more mana symbols, e.g. {3}{B}{G}
        |
        (?:[A-Za-z]+(?: [A-Za-z]+)*)       # word-based costs: "Sacrifice a creature"
    )
    \s*:\s*
    (?P<effect>.+)$
    """,
    re.IGNORECASE | re.VERBOSE
)

def derive_activated_abilities(axis1_card: Axis1Card) -> list[ActivatedAbility]:
    abilities = []
    text = axis1_card.faces[0].oracle_text or ""

    for raw in text.split("\n"):
        line = raw.replace("\u00A0", " ").strip()

        # NEW: strip wrapping parentheses
        if line.startswith("(") and line.endswith(")"):
            line = line[1:-1].strip()

        if not line:
            continue

        match = ACTIVATED_ABILITY_PATTERN.match(line)
        if not match:
            continue

        cost_str = match.group("cost").strip()
        effect_str = match.group("effect").strip()

        cost_objs = parse_cost_string(cost_str)
        effect_objs, is_mana = parse_effect_string(effect_str)

        abilities.append(
            ActivatedAbility(
                cost=cost_objs,
                effect=effect_objs,
                is_mana_ability=is_mana,
                restrictions=[],
            )
        )

    return abilities
