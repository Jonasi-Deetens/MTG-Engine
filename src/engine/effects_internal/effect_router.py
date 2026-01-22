"""Effect routing and dispatch."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from ..state import GameObject, GameState, ResolveContext

logger = logging.getLogger(__name__)


# Type alias for effect handler functions
EffectHandler = Callable[["EffectRouter", Dict[str, Any], "ResolveContext"], Dict[str, Any]]


@dataclass
class EffectResult:
    """Result of applying an effect."""

    type: str
    status: str
    data: Dict[str, Any]


class EffectRouter:
    """Routes effects to their handlers.

    Responsible for:
    - Dispatching effects to appropriate handlers
    - Managing effect handler registration
    - Handling effect-specific target overrides
    - Adding temporary effects to objects
    """

    def __init__(self, game_state: "GameState") -> None:
        self._game_state = game_state
        self._handlers: Dict[str, EffectHandler] = {}

    @property
    def game_state(self) -> "GameState":
        """Get the game state."""
        return self._game_state

    def register_handler(self, effect_type: str, handler: EffectHandler) -> None:
        """Register a handler for an effect type."""
        self._handlers[effect_type] = handler

    def register_handlers(self, handlers: Dict[str, EffectHandler]) -> None:
        """Register multiple handlers at once."""
        self._handlers.update(handlers)

    def apply(self, effect: Dict[str, Any], context: "ResolveContext") -> Dict[str, Any]:
        """Apply an effect using the appropriate handler.
        
        Supports per-effect conditions and optional flags:
        - If effect has a 'condition', it's evaluated before execution
        - If effect has 'optional: true' and condition fails, effect is skipped gracefully
        - If effect is not optional and condition fails, effect is skipped with status
        """
        effect_type = effect.get("type")
        handler = self._handlers.get(effect_type)

        if not handler:
            self._game_state.log(f"Unhandled effect type: {effect_type}")
            return {"type": effect_type, "status": "unhandled"}

        # Check per-effect condition if present
        effect_condition = effect.get("condition")
        is_optional = effect.get("optional", False)
        
        if effect_condition:
            from ..conditions import evaluate_condition
            condition_passed = evaluate_condition(self._game_state, effect_condition, context)
            
            node_id = effect.get("_node_id") or effect.get("node_id", "unknown")
            self._game_state.log(
                f"[effect] per-effect condition check node={node_id} "
                f"type={effect_condition.get('type')} passed={condition_passed}"
            )
            print(
                f"[graph] per-effect condition check node={node_id} "
                f"type={effect_condition.get('type')} passed={condition_passed}",
                flush=True
            )
            
            if not condition_passed:
                if is_optional:
                    # Optional effect with failed condition - skip gracefully
                    self._game_state.log(f"[effect] optional effect skipped (condition failed): {effect_type}")
                    return {"type": effect_type, "status": "skipped_optional", "reason": "condition_failed"}
                else:
                    # Required effect with failed condition - skip with status
                    self._game_state.log(f"[effect] effect skipped (condition failed): {effect_type}")
                    return {"type": effect_type, "status": "condition_failed"}

        # Handle effect-specific target overrides
        node_id = effect.get("_node_id") or effect.get("node_id")
        original_targets = context.targets
        if node_id and context.targets_by_effect.get(node_id):
            context.targets = context.targets_by_effect[node_id]

        try:
            result = handler(self, effect, context)
        finally:
            context.targets = original_targets

        return result

    def add_temporary_effect(self, obj: "GameObject", effect: Dict[str, Any]) -> None:
        """Add a temporary effect to an object."""
        if "controller_id" not in effect:
            effect["controller_id"] = obj.controller_id
        if "timestamp" not in effect:
            effect["timestamp"] = self._game_state.turn.turn_number
        if "timestamp_order" not in effect:
            self._game_state.effect_timestamp_counter += 1
            effect["timestamp_order"] = self._game_state.effect_timestamp_counter
        obj.temporary_effects.append(effect)

    # Alias for backward compatibility with effect handlers
    _add_temporary_effect = add_temporary_effect

    def log(self, message: str) -> None:
        """Log a message through the game state."""
        self._game_state.log(message)


def create_default_router(game_state: "GameState") -> EffectRouter:
    """Create an EffectRouter with all default handlers registered."""
    from ..effects_basic import (
        handle_add_poison,
        handle_counters,
        handle_discard,
        handle_draw,
        handle_draw_each,
        handle_fight,
        handle_life,
        handle_lose_life,
        handle_look_at,
        handle_mana,
        handle_mill,
        handle_reveal,
        handle_scry,
        handle_token,
    )
    from ..effects_copy import (
        handle_copy_permanent,
        handle_copy_spell,
        handle_enter_choice,
        handle_enter_copy,
    )
    from ..effects_damage import handle_damage, handle_prevent_damage, handle_redirect_damage
    from ..effects_replacements import (
        handle_replace_destroy,
        handle_replace_discard,
        handle_replace_draw,
        handle_replace_life_loss,
        handle_replace_sacrifice,
        handle_replace_zone_change,
    )
    from ..effects_types import (
        handle_add_color,
        handle_add_type,
        handle_append_oracle_text,
        handle_cda_power_toughness,
        handle_change_power_toughness,
        handle_gain_keyword,
        handle_modify_cast_cost,
        handle_protection,
        handle_remove_oracle_text,
        handle_remove_color,
        handle_remove_type,
        handle_set_colors,
        handle_set_oracle_text,
        handle_set_types,
    )
    from ..effects_zone import (
        handle_attach,
        handle_change_control,
        handle_counter_spell,
        handle_destroy,
        handle_exile,
        handle_flicker,
        handle_phase_out,
        handle_put_onto_battlefield,
        handle_regenerate,
        handle_return,
        handle_sacrifice,
        handle_search,
        handle_shuffle,
        handle_tap,
        handle_transform,
        handle_untap,
    )

    router = EffectRouter(game_state)
    router.register_handlers({
        "damage": handle_damage,
        "draw": handle_draw,
        "draw_each": handle_draw_each,
        "token": handle_token,
        "counters": handle_counters,
        "life": handle_life,
        "lose_life": handle_lose_life,
        "add_poison": handle_add_poison,
        "mana": handle_mana,
        "untap": handle_untap,
        "tap": handle_tap,
        "destroy": handle_destroy,
        "exile": handle_exile,
        "return": handle_return,
        "sacrifice": handle_sacrifice,
        "search": handle_search,
        "put_onto_battlefield": handle_put_onto_battlefield,
        "attach": handle_attach,
        "shuffle": handle_shuffle,
        "protection": handle_protection,
        "gain_keyword": handle_gain_keyword,
        "change_power_toughness": handle_change_power_toughness,
        "fight": handle_fight,
        "mill": handle_mill,
        "discard": handle_discard,
        "scry": handle_scry,
        "look_at": handle_look_at,
        "reveal": handle_reveal,
        "copy_spell": handle_copy_spell,
        "enter_copy": handle_enter_copy,
        "enter_choice": handle_enter_choice,
        "copy_permanent": handle_copy_permanent,
        "counter_spell": handle_counter_spell,
        "regenerate": handle_regenerate,
        "phase_out": handle_phase_out,
        "transform": handle_transform,
        "flicker": handle_flicker,
        "change_control": handle_change_control,
        "prevent_damage": handle_prevent_damage,
        "redirect_damage": handle_redirect_damage,
        "replace_zone_change": handle_replace_zone_change,
        "replace_destroy": handle_replace_destroy,
        "replace_sacrifice": handle_replace_sacrifice,
        "replace_draw": handle_replace_draw,
        "replace_discard": handle_replace_discard,
        "replace_life_loss": handle_replace_life_loss,
        "set_types": handle_set_types,
        "add_type": handle_add_type,
        "remove_type": handle_remove_type,
        "set_colors": handle_set_colors,
        "add_color": handle_add_color,
        "remove_color": handle_remove_color,
        "cda_power_toughness": handle_cda_power_toughness,
        "set_oracle_text": handle_set_oracle_text,
        "append_oracle_text": handle_append_oracle_text,
        "remove_oracle_text": handle_remove_oracle_text,
        "modify_cast_cost": handle_modify_cast_cost,
    })

    return router
