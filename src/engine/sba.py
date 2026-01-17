from __future__ import annotations

from .state import GameState
from .zones import ZONE_BATTLEFIELD


def apply_state_based_actions(game_state: GameState) -> None:
    _apply_legend_rule(game_state)
    _apply_counter_cancellation(game_state)
    _apply_planeswalker_uniqueness(game_state)
    _apply_attachment_checks(game_state)
    _cleanup_tokens_in_zones(game_state)

    for obj in list(game_state.objects.values()):
        if obj.zone != ZONE_BATTLEFIELD:
            continue
        if obj.phased_out:
            continue
        if obj.toughness is not None and obj.toughness <= 0:
            game_state.destroy_object(obj.id, allow_regen=False)
            continue
        if obj.toughness is not None and obj.damage >= obj.toughness:
            if "Indestructible" not in obj.keywords:
                game_state.destroy_object(obj.id, allow_regen=True)
        if "Planeswalker" in obj.types:
            if obj.counters.get("loyalty", 0) <= 0:
                game_state.destroy_object(obj.id, allow_regen=False)

    for player in game_state.players:
        if player.life <= 0:
            if not player.has_lost:
                player.has_lost = True
                game_state.log(f"Player {player.id} has 0 or less life.")
            if not player.removed_from_game:
                game_state.remove_player_from_game(player.id)
        if player.poison_counters >= 10:
            if not player.has_lost:
                player.has_lost = True
                game_state.log(f"Player {player.id} has 10 or more poison counters.")
            if not player.removed_from_game:
                game_state.remove_player_from_game(player.id)
        if any(damage >= 21 for damage in player.commander_damage_taken.values()):
            if not player.has_lost:
                player.has_lost = True
                game_state.log(f"Player {player.id} has 21 or more commander damage.")
            if not player.removed_from_game:
                game_state.remove_player_from_game(player.id)


def _apply_legend_rule(game_state: GameState) -> None:
    legend_groups = {}
    for obj in game_state.objects.values():
        if obj.zone != ZONE_BATTLEFIELD:
            continue
        if "Legendary" not in obj.types:
            continue
        legend_groups.setdefault((obj.controller_id, obj.name), []).append(obj)

    for (_, _), group in legend_groups.items():
        if len(group) <= 1:
            continue
        keep = max(
            enumerate(group),
            key=lambda item: ((item[1].entered_turn or -1), item[0]),
        )[1]
        for obj in group:
            if obj.id == keep.id:
                continue
            game_state.destroy_object(obj.id, allow_regen=False)


def _apply_counter_cancellation(game_state: GameState) -> None:
    for obj in game_state.objects.values():
        if obj.zone != ZONE_BATTLEFIELD:
            continue
        counters = obj.counters or {}
        plus = counters.get("+1/+1", 0)
        minus = counters.get("-1/-1", 0)
        if plus <= 0 or minus <= 0:
            continue
        cancel = min(plus, minus)
        counters["+1/+1"] = plus - cancel
        counters["-1/-1"] = minus - cancel


def _apply_planeswalker_uniqueness(game_state: GameState) -> None:
    planeswalker_groups = {}
    for obj in game_state.objects.values():
        if obj.zone != ZONE_BATTLEFIELD:
            continue
        if "Planeswalker" not in obj.types:
            continue
        planeswalker_groups.setdefault((obj.controller_id, obj.name), []).append(obj)

    for (_, _), group in planeswalker_groups.items():
        if len(group) <= 1:
            continue
        keep = max(
            enumerate(group),
            key=lambda item: ((item[1].entered_turn or -1), item[0]),
        )[1]
        for obj in group:
            if obj.id == keep.id:
                continue
            game_state.destroy_object(obj.id, allow_regen=False)


def _apply_attachment_checks(game_state: GameState) -> None:
    for obj in list(game_state.objects.values()):
        if obj.zone != ZONE_BATTLEFIELD:
            continue
        moved = game_state._enforce_attachment_legality(obj)
        if moved:
            continue


def _is_illegal_attachment(game_state: GameState, aura, attached) -> bool:
    return game_state._is_illegal_attachment(aura, attached)


def _cleanup_tokens_in_zones(game_state: GameState) -> None:
    to_remove = []
    for obj in game_state.objects.values():
        if not obj.is_token:
            continue
        if obj.zone != ZONE_BATTLEFIELD:
            to_remove.append(obj.id)
    for obj_id in to_remove:
        obj = game_state.objects.get(obj_id)
        if not obj:
            continue
        game_state._remove_from_zone(obj.zone, obj_id)
        del game_state.objects[obj_id]

