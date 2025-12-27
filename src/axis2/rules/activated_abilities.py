import re

from axis1.schema import Axis1Card, Axis1ActivatedAbility
from axis2.schema import ActivatedAbility

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
    text = axis1_card.faces[0].oracle_text

    for raw in text.split("\n"):
        line = raw.replace("\u00A0", " ").strip()
        if not line:
            continue

        match = ACTIVATED_ABILITY_PATTERN.match(line)
        if match:
            cost = match.group("cost").strip()
            effect = match.group("effect").strip()

            abilities.append(
                ActivatedAbility(
                    cost=cost,
                    effect_text=effect,
                    restrictions=[],
                )
            )

    return abilities
