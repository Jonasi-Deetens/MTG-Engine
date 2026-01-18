from __future__ import annotations

from typing import Any, Dict, List

from .effects_helpers import (
    resolve_target_objects,
    resolve_target_players,
    resolve_effect_players,
    resolve_choice_for_player,
    resolve_target_list_for_player,
)
from .replacements import resolve_replacement, apnap_player_order
from .state import ResolveContext
from .targets import resolve_object_id, resolve_player_id
from .zones import ZONE_GRAVEYARD, ZONE_HAND, ZONE_LIBRARY


def _draw_for_player(resolver, player_id: int, amount: int) -> Dict[str, Any]:
    player = resolver.game_state.get_player(player_id)
    drawn = []
    replaced = []
    for _ in range(amount):
        if not player.library:
            player.has_lost = True
            resolver.game_state.log(f"Player {player.id} loses for drawing from empty library.")
            if not player.removed_from_game:
                resolver.game_state.remove_player_from_game(player.id)
            break
        card_id = player.library[0]
        replacement = resolve_replacement(
            resolver.game_state,
            "replace_draw",
            player_id,
            f"draw:event:player:{player_id}",
            consume_choice=False,
        )
        if replacement and replacement.get("replacement_zone") == "skip":
            continue
        destination = replacement.get("replacement_zone") if replacement else ZONE_HAND
        resolver.game_state.move_object(card_id, destination)
        if destination == ZONE_HAND:
            drawn.append(card_id)
        else:
            replaced.append({"card_id": card_id, "zone": destination})
    return {"player_id": player_id, "cards": drawn, "replaced": replaced}


def handle_draw(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "draw", "status": "no_player"}
    ordered = apnap_player_order(resolver.game_state, player_ids) if len(player_ids) > 1 else player_ids
    results = [_draw_for_player(resolver, player_id, amount) for player_id in ordered]
    return {"type": "draw", "results": results} if len(results) > 1 else {"type": "draw", **results[0]}


def handle_draw_each(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    player_ids = [player.id for player in resolver.game_state.players if not getattr(player, "removed_from_game", False)]
    ordered = apnap_player_order(resolver.game_state, player_ids) if len(player_ids) > 1 else player_ids
    results = [_draw_for_player(resolver, player_id, amount) for player_id in ordered]
    return {"type": "draw_each", "results": results}


def handle_token(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    tokens = []
    for _ in range(amount):
        token = resolver.game_state.create_token(
            name="Token",
            controller_id=context.controller_id or 0,
            power=effect.get("power"),
            toughness=effect.get("toughness"),
            types=["Creature", "Token"],
        )
        tokens.append(token.id)
    return {"type": "token", "created": tokens}


def handle_counters(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    counter_type = effect.get("counterType", "+1/+1")
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "self")):
        obj.counters[counter_type] = obj.counters.get(counter_type, 0) + amount
        results.append({"object_id": obj.id, "counter": counter_type, "amount": amount})
    if not results:
        return {"type": "counters", "status": "no_target"}
    return {"type": "counters", "results": results}


def handle_life(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 0))
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "life", "status": "no_player"}
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        player.life += amount
        results.append({"player_id": player_id, "amount": amount})
    return {"type": "life", "results": results} if len(results) > 1 else {"type": "life", **results[0]}


def handle_lose_life(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 0))
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "lose_life", "status": "no_player"}
    results = []
    for player_id in player_ids:
        replacement = resolve_replacement(
            resolver.game_state,
            "replace_life_loss",
            player_id,
            f"life_loss:event:player:{player_id}",
            consume_choice=False,
        )
        replacement_amount = amount
        if replacement and (replacement.get("replacement_amount") is not None or replacement.get("replacementAmount") is not None):
            replacement_amount = int(replacement.get("replacement_amount") or replacement.get("replacementAmount") or amount)
        if replacement_amount <= 0:
            results.append({"player_id": player_id, "amount": 0})
            continue
        player = resolver.game_state.get_player(player_id)
        player.life -= replacement_amount
        results.append({"player_id": player_id, "amount": replacement_amount})
    return {"type": "lose_life", "results": results} if len(results) > 1 else {"type": "lose_life", **results[0]}


def handle_add_poison(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 0))
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "add_poison", "status": "no_player"}
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        player.poison_counters += amount
        results.append({"player_id": player_id, "amount": amount})
    return {"type": "add_poison", "results": results} if len(results) > 1 else {"type": "add_poison", **results[0]}


def handle_mana(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    mana_type = effect.get("manaType", "C")
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "mana", "status": "no_player"}
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        player.mana_pool[mana_type] = player.mana_pool.get(mana_type, 0) + amount
        results.append({"player_id": player_id, "mana_type": mana_type, "amount": amount})
    return {"type": "mana", "results": results} if len(results) > 1 else {"type": "mana", **results[0]}


def handle_fight(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    your_id = resolve_object_id(context, "yourCreature", None)
    opp_id = resolve_object_id(context, "opponentCreature", None)
    if not your_id or not opp_id:
        return {"type": "fight", "status": "no_target"}
    your_obj = resolver.game_state.objects.get(your_id)
    opp_obj = resolver.game_state.objects.get(opp_id)
    if not your_obj or not opp_obj:
        return {"type": "fight", "status": "invalid_target"}
    your_power = your_obj.power or 0
    opp_power = opp_obj.power or 0
    your_obj.damage += opp_power
    opp_obj.damage += your_power
    return {"type": "fight", "your": your_id, "opponent": opp_id}


def handle_mill(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "mill", "status": "no_player"}
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        milled = []
        for _ in range(amount):
            if not player.library:
                break
            card_id = player.library[0]
            resolver.game_state.move_object(card_id, ZONE_GRAVEYARD)
            milled.append(card_id)
        results.append({"player_id": player_id, "cards": milled})
    return {"type": "mill", "results": results} if len(results) > 1 else {"type": "mill", **results[0]}


def handle_discard(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "discard", "status": "no_player"}
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        discarded = []
        choices = resolve_choice_for_player(context.choices, "discard_ids", player_id)
        if not isinstance(choices, list):
            choices = resolve_target_list_for_player(context, "discard_ids", player_id)
        choices = list(choices or [])
        for _ in range(amount):
            if not player.hand:
                break
            if choices:
                card_id = choices.pop(0)
                if card_id not in player.hand:
                    continue
            else:
                card_id = player.hand[0]
            replacement = resolve_replacement(
                resolver.game_state,
                "replace_discard",
                player_id,
                f"discard:event:player:{player_id}",
                consume_choice=False,
            )
            if replacement and replacement.get("replacement_zone") == "skip":
                continue
            destination = replacement.get("replacement_zone") if replacement else ZONE_GRAVEYARD
            resolver.game_state.move_object(card_id, destination)
            discarded.append(card_id)
        results.append({"player_id": player_id, "cards": discarded})
    return {"type": "discard", "results": results} if len(results) > 1 else {"type": "discard", **results[0]}


def handle_scry(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "scry", "status": "no_player"}
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        scryed = list(player.library[:amount])
        if not scryed:
            results.append({"player_id": player_id, "cards": []})
            continue
        choice = resolve_choice_for_player(context.choices, "scry", player_id)
        if isinstance(choice, dict):
            chosen_top = choice.get("top") or []
            chosen_bottom = choice.get("bottom") or []
            if (
                isinstance(chosen_top, list)
                and isinstance(chosen_bottom, list)
                and set(chosen_top + chosen_bottom).issubset(set(scryed))
            ):
                remaining = [card_id for card_id in scryed if card_id not in chosen_top + chosen_bottom]
                new_top = [card_id for card_id in chosen_top if card_id in scryed] + remaining
                new_bottom = [card_id for card_id in chosen_bottom if card_id in scryed]
                player.library = new_top + player.library[amount:] + new_bottom
        results.append({"player_id": player_id, "cards": scryed})
    return {"type": "scry", "results": results} if len(results) > 1 else {"type": "scry", **results[0]}


def handle_look_at(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    zone = effect.get("zone", ZONE_LIBRARY)
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "look_at", "status": "no_player"}
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        pool = getattr(player, zone, [])
        results.append({"player_id": player_id, "zone": zone, "cards": pool[:amount]})
    return {"type": "look_at", "results": results} if len(results) > 1 else {"type": "look_at", **results[0]}


def handle_reveal(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    target = resolve_object_id(context, "target", None)
    return {"type": "reveal", "target": target}

