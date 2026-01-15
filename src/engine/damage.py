from __future__ import annotations

from typing import Optional, List, Tuple

from .state import GameObject, GameState


def _apply_prevent_damage(target: GameObject, amount: int) -> int:
    remaining = amount
    new_effects = []
    for effect in target.temporary_effects:
        prevent_amount = effect.get("prevent_damage")
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
            updated["prevent_damage"] = leftover
            new_effects.append(updated)
    target.temporary_effects = new_effects
    return remaining


def _apply_redirect_damage(
    game_state: GameState,
    source: GameObject,
    target: GameObject,
    amount: int,
) -> Tuple[List[Tuple[GameObject, int]], int]:
    remaining = amount
    redirected: List[Tuple[GameObject, int]] = []
    for effect in list(game_state.replacement_effects):
        if effect.get("type") != "redirect_damage":
            continue
        if effect.get("source") != source.id:
            continue
        redirect_id = effect.get("redirect")
        redirect_target = game_state.objects.get(redirect_id)
        if not redirect_target:
            continue
        available = int(effect.get("amount", remaining))
        if available <= 0:
            continue
        redirect_amount = min(remaining, available)
        if redirect_amount <= 0:
            continue
        redirected.append((redirect_target, redirect_amount))
        remaining -= redirect_amount
        if "amount" in effect:
            effect["amount"] = max(0, available - redirect_amount)
            if effect["amount"] <= 0:
                game_state.replacement_effects.remove(effect)
        if remaining <= 0:
            break
    return redirected, remaining


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
    remaining = _apply_prevent_damage(target, amount)
    if remaining <= 0:
        return
    target.damage += remaining
    if "Deathtouch" in source.keywords:
        target.damage = max(target.damage, target.toughness or target.damage)


def apply_damage_to_object(
    game_state: GameState,
    source: GameObject,
    target: GameObject,
    amount: int,
) -> None:
    if amount <= 0:
        return
    redirected, remaining = _apply_redirect_damage(game_state, source, target, amount)
    for redirect_target, redirect_amount in redirected:
        _apply_damage_to_object_target(game_state, source, redirect_target, redirect_amount)
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
    player = game_state.get_player(player_id)
    player.life -= amount
    if "Lifelink" in source.keywords:
        controller = game_state.get_player(source.controller_id)
        controller.life += amount

