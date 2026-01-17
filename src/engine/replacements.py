from __future__ import annotations

from typing import Dict, List, Optional

from .state import GameState


def _sort_key(effect: Dict) -> int:
    return int(effect.get("timestamp_order", 0))


def _consume_effect(effect: Dict, container: List[Dict]) -> None:
    uses = effect.get("uses")
    if uses is None:
        return
    remaining = int(uses) - 1
    if remaining <= 0:
        container.remove(effect)
    else:
        effect["uses"] = remaining


def _choose_effect(game_state: GameState, effects: List[Dict], event_key: str) -> Optional[Dict]:
    if not effects:
        return None
    if len(effects) == 1:
        return effects[0]
    choice_id = game_state.replacement_choices.get(event_key)
    if choice_id:
        for effect in effects:
            if effect.get("effect_id") == choice_id:
                return effect
    game_state.log(f"Multiple replacements for {event_key}; defaulted to most recent.")
    return max(effects, key=_sort_key)


def resolve_replacement(
    game_state: GameState,
    effect_type: str,
    player_id: Optional[int],
    event_key: str,
    consume_choice: bool = True,
) -> Optional[Dict]:
    effects = [
        effect
        for effect in list(game_state.replacement_effects)
        if effect.get("type") == effect_type
        and (effect.get("player_id") is None or effect.get("player_id") == player_id)
    ]
    chosen = _choose_effect(game_state, effects, event_key)
    if not chosen:
        return None
    _consume_effect(chosen, game_state.replacement_effects)
    if consume_choice:
        game_state.replacement_choices.pop(event_key, None)
    return chosen

