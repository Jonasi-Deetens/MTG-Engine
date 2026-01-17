from __future__ import annotations

from typing import Optional, List, Tuple

from .commander import record_commander_damage
from .state import GameObject, GameState


def _prioritize_choice(effects: List[dict], choice_id: Optional[str]) -> List[dict]:
    if not effects:
        return effects
    if choice_id:
        for idx, effect in enumerate(effects):
            if effect.get("effect_id") == choice_id:
                return [effects[idx]] + effects[:idx] + effects[idx + 1 :]
    return effects


def _most_recent_timestamp(effects: List[dict]) -> int:
    if not effects:
        return -1
    return max(int(effect.get("timestamp_order", 0)) for effect in effects)


def _select_damage_replacement_preference(
    game_state: GameState,
    event_key: str,
    redirect_effects: List[dict],
    prevent_effects: List[dict],
) -> Optional[str]:
    choice_id = game_state.replacement_choices.get(event_key)
    if choice_id:
        if any(effect.get("effect_id") == choice_id for effect in redirect_effects):
            return "redirect"
        if any(effect.get("effect_id") == choice_id for effect in prevent_effects):
            return "prevent"
    if not redirect_effects and not prevent_effects:
        return None
    if _most_recent_timestamp(prevent_effects) >= _most_recent_timestamp(redirect_effects):
        return "prevent"
    return "redirect"


def _collect_redirect_effects(game_state: GameState, source: GameObject) -> List[dict]:
    return [
        effect
        for effect in list(game_state.replacement_effects)
        if effect.get("type") == "redirect_damage" and effect.get("source") == source.id
    ]


def _collect_prevent_effects_for_object(target: GameObject) -> List[dict]:
    return [effect for effect in target.temporary_effects if effect.get("prevent_damage") is not None]


def _collect_prevent_effects_for_player(game_state: GameState, player_id: int) -> List[dict]:
    return [
        effect
        for effect in list(game_state.replacement_effects)
        if effect.get("type") == "prevent_damage" and effect.get("player_id") == player_id
    ]


def _apply_prevent_damage(game_state: GameState, target: GameObject, amount: int) -> int:
    remaining = amount
    new_effects = []
    prevent_effects = [effect for effect in target.temporary_effects if effect.get("prevent_damage") is not None]
    other_effects = [effect for effect in target.temporary_effects if effect.get("prevent_damage") is None]
    prevent_effects.sort(key=lambda effect: int(effect.get("timestamp_order", 0)), reverse=True)
    if len(prevent_effects) > 1:
        choice_key = f"damage:prevent:object:{target.id}"
        choice_id = game_state.replacement_choices.get(choice_key)
        prevent_effects = _prioritize_choice(prevent_effects, choice_id)
    for effect in prevent_effects:
        prevent_amount = effect.get("prevent_damage")
        if remaining <= 0:
            new_effects.append(effect)
            continue
        used = min(int(prevent_amount), remaining)
        remaining -= used
        leftover = int(prevent_amount) - used
        if leftover > 0:
            updated = dict(effect)
            updated["prevent_damage"] = leftover
            new_effects.append(updated)
    target.temporary_effects = other_effects + new_effects
    return remaining


def _apply_prevent_damage_to_player(game_state: GameState, player_id: int, amount: int) -> int:
    remaining = amount
    new_effects = []
    prevent_effects = [
        effect for effect in list(game_state.replacement_effects)
        if effect.get("type") == "prevent_damage" and effect.get("player_id") == player_id
    ]
    prevent_effects.sort(key=lambda effect: int(effect.get("timestamp_order", 0)), reverse=True)
    if len(prevent_effects) > 1:
        choice_key = f"damage:prevent:player:{player_id}"
        choice_id = game_state.replacement_choices.get(choice_key)
        prevent_effects = _prioritize_choice(prevent_effects, choice_id)
    other_effects = [
        effect for effect in list(game_state.replacement_effects)
        if effect.get("type") != "prevent_damage" or effect.get("player_id") != player_id
    ]
    for effect in prevent_effects:
        if effect.get("type") != "prevent_damage":
            new_effects.append(effect)
            continue
        if effect.get("player_id") != player_id:
            new_effects.append(effect)
            continue
        prevent_amount = effect.get("amount")
        if prevent_amount is None:
            new_effects.append(effect)
            continue
        if remaining <= 0:
            new_effects.append(effect)
            continue
        used = min(int(prevent_amount), remaining)
        remaining -= used
        leftover = int(prevent_amount) - used
        if leftover > 0:
            updated = dict(effect)
            updated["amount"] = leftover
            new_effects.append(updated)
    game_state.replacement_effects = other_effects + new_effects
    return remaining


def _apply_redirect_damage(
    game_state: GameState,
    source: GameObject,
    amount: int,
) -> Tuple[List[Tuple[GameObject, int]], List[Tuple[int, int]], int]:
    remaining = amount
    redirected: List[Tuple[GameObject, int]] = []
    redirected_players: List[Tuple[int, int]] = []
    matching_effects = [
        effect for effect in list(game_state.replacement_effects)
        if effect.get("type") == "redirect_damage" and effect.get("source") == source.id
    ]
    matching_effects.sort(key=lambda effect: int(effect.get("timestamp_order", 0)), reverse=True)
    if len(matching_effects) > 1:
        choice_key = f"damage:redirect:{source.id}"
        choice_id = game_state.replacement_choices.get(choice_key)
        matching_effects = _prioritize_choice(matching_effects, choice_id)
    for effect in matching_effects:
        if effect.get("type") != "redirect_damage":
            continue
        if effect.get("source") != source.id:
            continue
        redirect_id = effect.get("redirect")
        redirect_player_id = effect.get("redirect_player_id")
        redirect_target = game_state.objects.get(redirect_id) if redirect_id else None
        if not redirect_target and redirect_player_id is None:
            continue
        available = int(effect.get("amount", remaining))
        if available <= 0:
            continue
        redirect_amount = min(remaining, available)
        if redirect_amount <= 0:
            continue
        if redirect_target:
            redirected.append((redirect_target, redirect_amount))
        else:
            redirected_players.append((redirect_player_id, redirect_amount))
        remaining -= redirect_amount
        if "amount" in effect:
            effect["amount"] = max(0, available - redirect_amount)
            if effect["amount"] <= 0:
                game_state.replacement_effects.remove(effect)
        if remaining <= 0:
            break
    return redirected, redirected_players, remaining


def _apply_damage_to_object_target(
    game_state: GameState,
    source: GameObject,
    target: GameObject,
    amount: int,
) -> None:
    if amount <= 0:
        return
    if target.protections:
        if any(color in target.protections for color in source.colors):
            return
    remaining = _apply_prevent_damage(game_state, target, amount)
    if remaining <= 0:
        return
    if "Planeswalker" in target.types:
        counters = target.counters or {}
        current = int(counters.get("loyalty", 0))
        counters["loyalty"] = max(0, current - remaining)
        target.counters = counters
        return
    if "Infect" in source.keywords:
        counters = target.counters or {}
        if "Deathtouch" in source.keywords and (target.toughness or 0) > remaining:
            remaining = target.toughness or remaining
        counters["-1/-1"] = counters.get("-1/-1", 0) + remaining
        target.counters = counters
        return
    target.damage += remaining
    if "Deathtouch" in source.keywords:
        target.damage = max(target.damage, target.toughness or target.damage)


def _apply_damage_to_player_target(
    game_state: GameState,
    source: GameObject,
    player_id: int,
    amount: int,
) -> None:
    if amount <= 0:
        return
    player = game_state.get_player(player_id)
    remaining = _apply_prevent_damage_to_player(game_state, player_id, amount)
    if remaining <= 0:
        return
    if "Infect" in source.keywords:
        player.poison_counters += remaining
    else:
        player.life -= remaining
    if _is_commander_source(game_state, source.id):
        record_commander_damage(game_state, source.id, player_id, remaining)
    if "Lifelink" in source.keywords:
        controller = game_state.get_player(source.controller_id)
        controller.life += remaining


def _is_commander_source(game_state: GameState, source_id: str) -> bool:
    return any(player.commander_id == source_id for player in game_state.players)


def apply_damage_to_object(
    game_state: GameState,
    source: GameObject,
    target: GameObject,
    amount: int,
) -> None:
    if amount <= 0:
        return
    redirect_effects = _collect_redirect_effects(game_state, source)
    prevent_effects = _collect_prevent_effects_for_object(target)
    event_key = f"damage:event:{source.id}:object:{target.id}"
    if len(redirect_effects) + len(prevent_effects) > 1:
        preference = _select_damage_replacement_preference(
            game_state,
            event_key,
            redirect_effects,
            prevent_effects,
        )
    else:
        preference = None

    if preference == "prevent":
        remaining = _apply_prevent_damage(game_state, target, amount)
        if remaining <= 0:
            return
        redirected, redirected_players, remaining = _apply_redirect_damage(game_state, source, remaining)
    else:
        redirected, redirected_players, remaining = _apply_redirect_damage(game_state, source, amount)

    for redirect_target, redirect_amount in redirected:
        _apply_damage_to_object_target(game_state, source, redirect_target, redirect_amount)
    for redirect_player_id, redirect_amount in redirected_players:
        _apply_damage_to_player_target(game_state, source, redirect_player_id, redirect_amount)
    if remaining > 0:
        _apply_damage_to_object_target(game_state, source, target, remaining)


def apply_damage_to_player(
    game_state: GameState,
    source: GameObject,
    player_id: int,
    amount: int,
) -> None:
    if amount <= 0:
        return
    redirect_effects = _collect_redirect_effects(game_state, source)
    prevent_effects = _collect_prevent_effects_for_player(game_state, player_id)
    event_key = f"damage:event:{source.id}:player:{player_id}"
    if len(redirect_effects) + len(prevent_effects) > 1:
        preference = _select_damage_replacement_preference(
            game_state,
            event_key,
            redirect_effects,
            prevent_effects,
        )
    else:
        preference = None

    if preference == "prevent":
        remaining = _apply_prevent_damage_to_player(game_state, player_id, amount)
        if remaining <= 0:
            return
        redirected, redirected_players, remaining = _apply_redirect_damage(game_state, source, remaining)
    else:
        redirected, redirected_players, remaining = _apply_redirect_damage(game_state, source, amount)

    for redirect_target, redirect_amount in redirected:
        _apply_damage_to_object_target(game_state, source, redirect_target, redirect_amount)
    for redirect_player_id, redirect_amount in redirected_players:
        _apply_damage_to_player_target(game_state, source, redirect_player_id, redirect_amount)
    if remaining > 0:
        _apply_damage_to_player_target(game_state, source, player_id, remaining)

