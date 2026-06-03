from __future__ import annotations

from .state import GameState
from .zones import ZONE_BATTLEFIELD


def apply_state_based_actions(game_state: GameState) -> None:
    max_iterations = 10
    previous_signature = None
    for _ in range(max_iterations):
        _apply_legend_rule(game_state)
        _apply_counter_cancellation(game_state)
        _apply_attachment_checks(game_state)
        _cleanup_tokens_in_zones(game_state)

        for obj in list(game_state.objects.values()):
            if obj.zone != ZONE_BATTLEFIELD:
                continue
            if obj.phased_out:
                continue
            if obj.toughness is not None and obj.toughness <= 0:
                game_state.state_based_put_into_graveyard(obj.id)
                continue
            if obj.toughness is not None and obj.damage >= obj.toughness:
                if "Indestructible" not in obj.keywords:
                    game_state.destroy_object(obj.id, allow_regen=True)
            if "Planeswalker" in obj.types:
                if obj.counters.get("loyalty", 0) <= 0:
                    game_state.state_based_put_into_graveyard(obj.id)

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

        signature = _sba_signature(game_state)
        if signature == previous_signature:
            break
        previous_signature = signature


def _controller_ignores_legend_rule(game_state: GameState, controller_id: int) -> bool:
    for active in list(game_state.active_effect_registry.effects):
        if active.controller_id != controller_id:
            continue
        body = active.effect_data.effect
        if getattr(body, "kind", None) != "continuous":
            continue
        modifier = getattr(body, "modifier", None)
        if modifier is None:
            continue
        if hasattr(modifier, "type"):
            modifier_type = getattr(modifier, "type", None)
        elif isinstance(modifier, dict):
            modifier_type = modifier.get("type")
        else:
            modifier_type = None
        if modifier_type == "ignore_legend_rule":
            return True
    return False


def _apply_legend_rule(game_state: GameState) -> None:
    legend_groups = {}
    for obj in game_state.objects.values():
        if obj.zone != ZONE_BATTLEFIELD:
            continue
        if "Legendary" not in obj.types:
            continue
        legend_groups.setdefault((obj.controller_id, obj.name), []).append(obj)

    for (controller_id, name), group in legend_groups.items():
        if len(group) <= 1:
            continue
        if _controller_ignores_legend_rule(game_state, controller_id):
            continue
        choice_key = f"legend_rule:{controller_id}:{name}"
        chosen_id = None
        if isinstance(game_state.choices, dict):
            chosen_id = game_state.choices.get(choice_key)
        keep = None
        if chosen_id and any(obj.id == chosen_id for obj in group):
            keep = next(obj for obj in group if obj.id == chosen_id)
        else:
            keep = max(
                enumerate(group),
                key=lambda item: ((item[1].entered_turn or -1), item[0]),
            )[1]
            pending = []
            if isinstance(game_state.choices, dict):
                pending = game_state.choices.get("pending", [])
                if not isinstance(pending, list):
                    pending = []
                pending.append({
                    "type": "legend_rule",
                    "key": choice_key,
                    "options": [obj.id for obj in group],
                })
                game_state.choices["pending"] = pending
            game_state.log(f"Legend rule choice missing for {name}; defaulted to {keep.id}.")
        for obj in group:
            if obj.id == keep.id:
                continue
            game_state.state_based_put_into_graveyard(obj.id)


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


def _apply_attachment_checks(game_state: GameState) -> None:
    for obj in list(game_state.objects.values()):
        if obj.zone != ZONE_BATTLEFIELD:
            continue
        moved = game_state.attachment_manager.enforce_legality(obj)
        if moved:
            continue


def _is_illegal_attachment(game_state: GameState, aura, attached) -> bool:
    return game_state.attachment_manager._is_illegal_attachment(aura, attached)


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
        game_state.zone_manager.remove_from_zone(obj.zone, obj_id)
        del game_state.objects[obj_id]


def _sba_signature(game_state: GameState) -> tuple:
    object_state = tuple(sorted(
        (obj.id, obj.zone, obj.damage, obj.toughness, obj.controller_id, tuple(sorted(obj.counters.items())))
        for obj in game_state.objects.values()
    ))
    player_state = tuple(
        (player.id, player.life, player.poison_counters, player.has_lost, player.removed_from_game)
        for player in game_state.players
    )
    return (object_state, player_state)

