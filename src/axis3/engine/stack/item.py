# axis3/rules/stack/item.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, Any

from axis3.engine.abilities.triggered import RuntimeTriggeredAbility
from axis3.engine.abilities.activated import RuntimeActivatedAbility
from axis3.engine.casting.context import CastContext


StackItemKind = Literal["spell", "activated_ability", "triggered_ability"]


@dataclass
class StackItem:
    """
    Represents a spell or ability on the stack.

    - Spells: obj_id + controller + CastContext
    - Activated abilities: activated_ability + controller + ability context
    - Triggered abilities: triggered_ability + controller + trigger context
    """

    kind: StackItemKind

    # Common fields
    controller: int
    payload: Optional[dict[str, Any]] = None

    # Spell fields
    source_id: Optional[str] = None
    cast_context: Optional[CastContext] = None

    # Ability fields
    triggered_ability: Optional[RuntimeTriggeredAbility] = None
    activated_ability: Optional[RuntimeActivatedAbility] = None

    # Optional X value for spells/abilities
    x_value: Optional[int] = None

    # ------------------------
    # Helper Methods
    # ------------------------

    def is_spell(self) -> bool:
        return self.kind == "spell"

    def is_triggered_ability(self) -> bool:
        return self.kind == "triggered_ability"

    def is_activated_ability(self) -> bool:
        return self.kind == "activated_ability"
