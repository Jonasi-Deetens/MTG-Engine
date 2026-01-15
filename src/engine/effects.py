from __future__ import annotations

from typing import Any, Dict, List, Optional
import random

from .state import GameState, ResolveContext, GameObject
from .zones import (
    ZONE_BATTLEFIELD,
    ZONE_COMMAND,
    ZONE_EXILE,
    ZONE_GRAVEYARD,
    ZONE_HAND,
    ZONE_LIBRARY,
)
from .targets import resolve_object, resolve_object_id, resolve_player_id
from .stack import StackItem


def _resolve_target_object(game_state: GameState, context: ResolveContext, target_key: str) -> Optional[GameObject]:
    fallback = context.source_id if target_key in ("self", "source") else None
    return resolve_object(game_state, context, target_key, fallback)


class EffectResolver:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def apply(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        effect_type = effect.get("type")
        handler = getattr(self, f"_handle_{effect_type}", None)
        if not handler:
            self.game_state.log(f"Unhandled effect type: {effect_type}")
            return {"type": effect_type, "status": "unhandled"}
        return handler(effect, context)

    def _handle_damage(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 0))
        target_type = effect.get("target", "any")
        if target_type in ("player", "any"):
            player_id = resolve_player_id(context, context.controller_id)
            if player_id is not None:
                player = self.game_state.get_player(player_id)
                player.life -= amount
                return {"type": "damage", "player_id": player_id, "amount": amount}
        obj = _resolve_target_object(self.game_state, context, target_type)
        if obj:
            obj.damage += amount
            return {"type": "damage", "object_id": obj.id, "amount": amount}
        return {"type": "damage", "status": "no_target"}

    def _handle_draw(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 1))
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "draw", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        drawn = []
        for _ in range(amount):
            if not player.library:
                break
            card_id = player.library.pop(0)
            player.hand.append(card_id)
            drawn.append(card_id)
        return {"type": "draw", "player_id": player_id, "cards": drawn}

    def _handle_token(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 1))
        tokens = []
        for _ in range(amount):
            token = self.game_state.create_token(
                name="Token",
                controller_id=context.controller_id or 0,
                power=effect.get("power"),
                toughness=effect.get("toughness"),
                types=["Creature", "Token"],
            )
            tokens.append(token.id)
        return {"type": "token", "created": tokens}

    def _handle_counters(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 1))
        counter_type = effect.get("counterType", "+1/+1")
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "self"))
        if not obj:
            return {"type": "counters", "status": "no_target"}
        obj.counters[counter_type] = obj.counters.get(counter_type, 0) + amount
        return {"type": "counters", "object_id": obj.id, "counter": counter_type, "amount": amount}

    def _handle_life(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 0))
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "life", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        player.life += amount
        return {"type": "life", "player_id": player_id, "amount": amount}

    def _handle_mana(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 1))
        mana_type = effect.get("manaType", "C")
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "mana", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        player.mana_pool[mana_type] = player.mana_pool.get(mana_type, 0) + amount
        return {"type": "mana", "player_id": player_id, "mana_type": mana_type, "amount": amount}

    def _handle_untap(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("untapTarget", "self"))
        if not obj:
            return {"type": "untap", "status": "no_target"}
        obj.tapped = False
        return {"type": "untap", "object_id": obj.id}

    def _handle_tap(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("untapTarget", "self"))
        if not obj:
            return {"type": "tap", "status": "no_target"}
        obj.tapped = True
        return {"type": "tap", "object_id": obj.id}

    def _handle_destroy(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        if not obj:
            return {"type": "destroy", "status": "no_target"}
        self.game_state.destroy_object(obj.id)
        return {"type": "destroy", "object_id": obj.id}

    def _handle_exile(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        if not obj:
            return {"type": "exile", "status": "no_target"}
        self.game_state.move_object(obj.id, ZONE_EXILE)
        return {"type": "exile", "object_id": obj.id}

    def _handle_return(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        if not obj:
            return {"type": "return", "status": "no_target"}
        self.game_state.move_object(obj.id, ZONE_HAND)
        return {"type": "return", "object_id": obj.id}

    def _handle_sacrifice(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        if not obj:
            return {"type": "sacrifice", "status": "no_target"}
        self.game_state.move_object(obj.id, ZONE_GRAVEYARD)
        return {"type": "sacrifice", "object_id": obj.id}

    def _handle_search(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        zone = effect.get("zone", ZONE_LIBRARY)
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "search", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        pool = getattr(player, zone, [])
        found_ids = context.targets.get("search_results", []) if isinstance(context.targets.get("search_results"), list) else []
        return {"type": "search", "zone": zone, "found": [obj_id for obj_id in found_ids if obj_id in pool]}

    def _handle_put_onto_battlefield(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        from_effect = effect.get("fromEffect")
        card_ids = []
        if from_effect is not None and from_effect < len(context.previous_results):
            card_ids = context.previous_results[from_effect].get("found", [])
        else:
            target_id = resolve_object_id(context, "target", None)
            if target_id:
                card_ids = [target_id]
        for obj_id in card_ids:
            self.game_state.move_object(obj_id, ZONE_BATTLEFIELD)
        return {"type": "put_onto_battlefield", "cards": card_ids}

    def _handle_attach(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        attach_to = resolve_object_id(context, "attach_to", effect.get("attachTo"))
        from_effect = effect.get("fromEffect")
        card_ids = []
        if from_effect is not None and from_effect < len(context.previous_results):
            card_ids = context.previous_results[from_effect].get("found", [])
        else:
            target_id = resolve_object_id(context, "target", None)
            if target_id:
                card_ids = [target_id]
        for obj_id in card_ids:
            obj = self.game_state.objects.get(obj_id)
            if obj:
                obj.attached_to = attach_to
        return {"type": "attach", "cards": card_ids, "attach_to": attach_to}

    def _handle_shuffle(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "shuffle", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        random.shuffle(player.library)
        return {"type": "shuffle", "player_id": player_id}

    def _handle_protection(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        if not obj:
            return {"type": "protection", "status": "no_target"}
        protection_type = effect.get("protectionType", "any")
        obj.protections.add(protection_type)
        return {"type": "protection", "object_id": obj.id, "protection": protection_type}

    def _handle_gain_keyword(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        keyword = effect.get("keyword")
        if not obj or not keyword:
            return {"type": "gain_keyword", "status": "no_target"}
        obj.keywords.add(keyword)
        return {"type": "gain_keyword", "object_id": obj.id, "keyword": keyword}

    def _handle_change_power_toughness(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_creature"))
        if not obj:
            return {"type": "change_power_toughness", "status": "no_target"}
        obj.power = (obj.power or 0) + int(effect.get("powerChange", 0))
        obj.toughness = (obj.toughness or 0) + int(effect.get("toughnessChange", 0))
        return {"type": "change_power_toughness", "object_id": obj.id}

    def _handle_fight(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        your_id = resolve_object_id(context, "yourCreature", None)
        opp_id = resolve_object_id(context, "opponentCreature", None)
        if not your_id or not opp_id:
            return {"type": "fight", "status": "no_target"}
        your_obj = self.game_state.objects.get(your_id)
        opp_obj = self.game_state.objects.get(opp_id)
        if not your_obj or not opp_obj:
            return {"type": "fight", "status": "invalid_target"}
        your_power = your_obj.power or 0
        opp_power = opp_obj.power or 0
        your_obj.damage += opp_power
        opp_obj.damage += your_power
        return {"type": "fight", "your": your_id, "opponent": opp_id}

    def _handle_mill(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 1))
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "mill", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        milled = []
        for _ in range(amount):
            if not player.library:
                break
            card_id = player.library.pop(0)
            player.graveyard.append(card_id)
            milled.append(card_id)
        return {"type": "mill", "player_id": player_id, "cards": milled}

    def _handle_discard(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 1))
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "discard", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        discarded = []
        choices = context.targets.get("discard_ids", [])
        for _ in range(amount):
            if not player.hand:
                break
            if choices:
                card_id = choices.pop(0)
                if card_id in player.hand:
                    player.hand.remove(card_id)
                else:
                    continue
            else:
                card_id = player.hand.pop(0)
            player.graveyard.append(card_id)
            discarded.append(card_id)
        return {"type": "discard", "player_id": player_id, "cards": discarded}

    def _handle_scry(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 1))
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "scry", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        scryed = player.library[:amount]
        return {"type": "scry", "player_id": player_id, "cards": scryed}

    def _handle_look_at(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        amount = int(effect.get("amount", 1))
        zone = effect.get("zone", ZONE_LIBRARY)
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return {"type": "look_at", "status": "no_player"}
        player = self.game_state.get_player(player_id)
        pool = getattr(player, zone, [])
        return {"type": "look_at", "zone": zone, "cards": pool[:amount]}

    def _handle_reveal(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        target = resolve_object_id(context, "target", None)
        return {"type": "reveal", "target": target}

    def _handle_copy_spell(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        target_spell = resolve_object_id(context, "target", None)
        if not target_spell:
            return {"type": "copy_spell", "status": "no_target"}
        self.game_state.stack.push(
            StackItem(kind="spell", payload={"copy_of": target_spell}, controller_id=context.controller_id)
        )
        return {"type": "copy_spell", "copy_of": target_spell}

    def _handle_regenerate(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_creature"))
        if not obj:
            return {"type": "regenerate", "status": "no_target"}
        obj.regenerate_shield = True
        return {"type": "regenerate", "object_id": obj.id}

    def _handle_phase_out(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        if not obj:
            return {"type": "phase_out", "status": "no_target"}
        obj.phased_out = True
        return {"type": "phase_out", "object_id": obj.id}

    def _handle_transform(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        if not obj:
            return {"type": "transform", "status": "no_target"}
        obj.transformed = not obj.transformed
        return {"type": "transform", "object_id": obj.id}

    def _handle_flicker(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        if not obj:
            return {"type": "flicker", "status": "no_target"}
        self.game_state.move_object(obj.id, ZONE_EXILE)
        self.game_state.move_object(obj.id, ZONE_BATTLEFIELD)
        return {"type": "flicker", "object_id": obj.id}

    def _handle_change_control(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        new_controller = context.targets.get("new_controller_id")
        if not obj or new_controller is None:
            return {"type": "change_control", "status": "no_target"}
        obj.controller_id = int(new_controller)
        return {"type": "change_control", "object_id": obj.id, "controller_id": obj.controller_id}

    def _handle_prevent_damage(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        obj = _resolve_target_object(self.game_state, context, effect.get("target", "target_permanent"))
        amount = int(effect.get("amount", 1))
        if not obj:
            return {"type": "prevent_damage", "status": "no_target"}
        obj.temporary_effects.append({"prevent_damage": amount})
        return {"type": "prevent_damage", "object_id": obj.id, "amount": amount}

    def _handle_redirect_damage(self, effect: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        source_id = resolve_object_id(context, "sourceTarget", None)
        redirect_id = resolve_object_id(context, "redirectTarget", None)
        amount = int(effect.get("amount", 1))
        if not source_id or not redirect_id:
            return {"type": "redirect_damage", "status": "no_target"}
        self.game_state.debug_log.append(
            f"Redirect {amount} damage from {source_id} to {redirect_id}"
        )
        return {"type": "redirect_damage", "source": source_id, "redirect": redirect_id, "amount": amount}
