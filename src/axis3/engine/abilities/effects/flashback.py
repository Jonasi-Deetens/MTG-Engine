# axis3/engine/abilities/effects/flashback.py

from dataclasses import dataclass
from typing import Optional
from axis3.engine.abilities.effects.base import Axis3Effect

@dataclass
class FlashbackEffect(Axis3Effect):
    flashback_cost: str = ""
    reduction_source: Optional[str] = None
    layering: str = "rules"

    def apply(self, game_state, source, controller):
        # 1. Allow casting from graveyard
        game_state.grant_permission(
            source=source,
            permission="may_cast_from_graveyard",
        )

        # 2. Register the alternative cost
        game_state.add_alternative_cost(
            source=source,
            cost=self.flashback_cost,
            tag="flashback",
        )

        # 3. Add cost reduction rule (if applicable)
        if self.reduction_source == "greatest_commander_mv":
            game_state.add_cost_reduction_rule(
                source=source,
                tag="flashback_reduction",
                amount_fn=lambda gs, ctrl: self._greatest_commander_mv(gs, ctrl),
                applies_if=lambda cast_ctx: cast_ctx.used_alternative_cost("flashback"),
            )

        # 4. Add replacement effect: exile on resolution if cast via flashback
        game_state.add_replacement_effect(
            source=source,
            tag="flashback_exile",
            applies_if=lambda ctx: ctx.used_alternative_cost("flashback"),
            effect_fn=lambda gs, spell: gs.move_to_zone(spell, "Exile"),
        )

        return True

    def _greatest_commander_mv(self, game_state, controller):
        commanders = game_state.get_commanders(controller)
        if not commanders:
            return 0
        return max(c.mana_value for c in commanders)
