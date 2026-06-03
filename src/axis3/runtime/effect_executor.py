from __future__ import annotations

import random
from typing import Any, List, Optional, Union

from axis2 import schema as a2
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.rules.atomic import draw as atomic_draw
from axis3.rules.atomic import damage as atomic_damage
from axis3.rules.atomic import life as atomic_life
from axis3.rules.sba.checker import run_sbas
from axis3.runtime.value_resolver import resolve_amount
from axis3.state.zones import ZoneType


EffectLike = Union[a2.Effect, Any]


class EffectExecutor:
    """Execute Axis2 structured effects against a GameState."""

    def __init__(self, game_state: Any):
        self.game_state = game_state
        self.subjects = game_state.subject_resolver

    def execute_all(
        self,
        effects: List[EffectLike],
        source_id: str,
        controller: int,
    ) -> None:
        for effect in effects or []:
            self.execute(effect, source_id, controller)

    def execute(
        self,
        effect: EffectLike,
        source_id: str,
        controller: int,
    ) -> bool:
        if effect is None:
            return False

        handler = self._handler_for(effect)
        if handler is None:
            self.game_state.add_debug_log(
                f"[EffectExecutor] No handler for {type(effect).__name__}"
            )
            return False
        return handler(effect, source_id, controller)

    def _handler_for(self, effect: EffectLike):
        mapping = {
            a2.DealDamageEffect: self._deal_damage,
            a2.DrawCardsEffect: self._draw_cards,
            a2.GainLifeEffect: self._gain_life,
            a2.DiscardEffect: self._discard,
            a2.AddManaEffect: self._add_mana,
            a2.DestroyEffect: self._destroy,
            a2.ChangeZoneEffect: self._change_zone,
            a2.CreateTokenEffect: self._create_token,
            a2.ScryEffect: self._scry,
            a2.SurveilEffect: self._surveil,
            a2.SearchEffect: self._search,
            a2.ShuffleEffect: self._shuffle,
            a2.RevealEffect: self._reveal,
            a2.TransformEffect: self._transform,
            a2.PutOntoBattlefieldEffect: self._put_onto_battlefield,
            a2.PutCounterEffect: self._put_counter,
            a2.AddCountersEffect: self._add_counters,
            a2.RemoveCounterEffect: self._remove_counter,
            a2.PTBoostEffect: self._pt_boost,
            a2.GainLifeEqualToPowerEffect: self._gain_life_equal_power,
            a2.ReturnCardFromGraveyardEffect: self._return_from_gy,
            a2.CounterSpellEffect: self._counter_spell,
            a2.ConditionalEffect: self._conditional,
            a2.LookAndPickEffect: self._look_and_pick,
            a2.Mode: self._mode,
            a2.GrantCastingPermissionEffect: self._grant_casting_permission,
            a2.StaticEffect: self._register_static,
            a2.ReplacementEffect: self._register_replacement,
            a2.ContinuousEffect: self._register_continuous,
            a2.EquipEffect: self._equip,
            a2.CantBeBlockedEffect: self._cant_be_blocked,
            a2.DayboundEffect: self._daybound,
            a2.NightboundEffect: self._nightbound,
            a2.DraftFromSpellbookEffect: self._draft_spellbook,
            a2.UnparsedOracleEffect: self._unparsed_oracle,
            a2.LoseLifeEffect: self._lose_life,
            a2.MillEffect: self._mill,
            a2.FightEffect: self._fight,
            a2.CopyEffect: self._copy,
            a2.ProliferateEffect: self._proliferate,
            a2.VentureEffect: self._venture,
        }
        for cls, fn in mapping.items():
            if isinstance(effect, cls):
                return fn
        return None

    # ─────────────────────────────────────────────────────────
    # One-shot effects
    # ─────────────────────────────────────────────────────────

    def _deal_damage(self, effect: a2.DealDamageEffect, source_id: str, controller: int) -> bool:
        amount = resolve_amount(
            effect.amount,
            game_state=self.game_state,
            source_id=source_id,
            controller=controller,
            default=0,
        )
        if amount <= 0:
            return True

        targets = self.subjects.resolve(effect.subject, source_id, controller)
        for target in targets:
            if hasattr(target, "life") and hasattr(target, "id"):
                atomic_life.apply_life_change(
                    self.game_state,
                    Event(
                        type=EventType.LIFE_CHANGE,
                        payload={
                            "player_id": target.id,
                            "amount": -amount,
                            "cause": source_id,
                        },
                    ),
                )
            elif hasattr(target, "id") and not hasattr(target, "life"):
                atomic_damage.apply_damage(
                    self.game_state,
                    Event(
                        type=EventType.DAMAGE,
                        payload={
                            "target_id": target.id,
                            "amount": amount,
                            "source_id": source_id,
                            "controller": controller,
                        },
                    ),
                )
        return True

    def _draw_cards(self, effect: a2.DrawCardsEffect, source_id: str, controller: int) -> bool:
        amount = resolve_amount(
            effect.amount,
            game_state=self.game_state,
            source_id=source_id,
            controller=controller,
            default=1,
        )
        atomic_draw.apply_draw(
            self.game_state,
            Event(
                type=EventType.DRAW,
                payload={
                    "player_id": controller,
                    "amount": amount,
                    "cause": source_id,
                },
            ),
        )
        return True

    def _gain_life(self, effect: a2.GainLifeEffect, source_id: str, controller: int) -> bool:
        amount = resolve_amount(
            effect.amount,
            game_state=self.game_state,
            source_id=source_id,
            controller=controller,
            default=0,
        )
        player_id = controller
        subj = (effect.subject or "you").lower()
        if "opponent" in subj:
            player_id = 1 - controller if len(self.game_state.players) == 2 else controller
        atomic_life.apply_life_change(
            self.game_state,
            Event(
                type=EventType.LIFE_CHANGE,
                payload={"player_id": player_id, "amount": amount, "cause": source_id},
            ),
        )
        return True

    def _discard(self, effect: a2.DiscardEffect, source_id: str, controller: int) -> bool:
        amount = resolve_amount(
            effect.amount,
            game_state=self.game_state,
            source_id=source_id,
            controller=controller,
            default=1,
        )
        for player in self.subjects.resolve(effect.subject, source_id, controller):
            if not hasattr(player, "hand"):
                continue
            pid = player.id
            for _ in range(amount):
                if not player.hand:
                    break
                card_id = player.hand.pop()
                self.game_state.zone_list(pid, "GRAVEYARD").append(card_id)
                obj = self.game_state.get_object(card_id)
                if obj:
                    obj.zone = ZoneType.GRAVEYARD
        return True

    def _add_mana(self, effect: a2.AddManaEffect, source_id: str, controller: int) -> bool:
        player = self.game_state.players[controller]
        for sym in effect.mana or []:
            sym = sym.strip("{}").upper()
            if sym in ("W", "U", "B", "R", "G", "C"):
                player.mana_pool[sym] = player.mana_pool.get(sym, 0) + 1
            elif sym.isdigit():
                player.mana_pool["C"] = player.mana_pool.get("C", 0) + int(sym)
        return True

    def _destroy(self, effect: a2.DestroyEffect, source_id: str, controller: int) -> bool:
        for obj_id in self.subjects.resolve_object_ids(
            effect.subject, source_id, controller, zone="BATTLEFIELD"
        ):
            obj = self.game_state.get_object(obj_id)
            if not obj:
                continue
            if getattr(obj, "is_token", False):
                self._move_object(obj_id, "BATTLEFIELD", None, obj.controller)
                del self.game_state.objects[obj_id]
            else:
                self._move_object(obj_id, "BATTLEFIELD", "GRAVEYARD", obj.controller)
        run_sbas(self.game_state)
        return True

    def _change_zone(self, effect: a2.ChangeZoneEffect, source_id: str, controller: int) -> bool:
        to_zone = (effect.to_zone or "graveyard").upper()
        from_zone = (effect.from_zone or "battlefield").upper()

        for obj_id in self.subjects.resolve_object_ids(
            effect.subject, source_id, controller, zone=from_zone
        ):
            obj = self.game_state.get_object(obj_id)
            if not obj:
                continue
            ctrl = obj.controller
            if effect.owner == "you":
                ctrl = controller
            self._move_object(obj_id, from_zone, to_zone, ctrl, tapped=effect.tapped)
            if effect.counters:
                for ctype, count in effect.counters.items():
                    obj.counters[ctype] = obj.counters.get(ctype, 0) + count
        return True

    def _create_token(self, effect: a2.CreateTokenEffect, source_id: str, controller: int) -> bool:
        amount = resolve_amount(
            effect.amount,
            game_state=self.game_state,
            source_id=source_id,
            controller=controller,
            default=1,
        )
        token_ctrl = controller
        if (effect.controller or "you").lower() in ("opponent", "target_opponent"):
            token_ctrl = 1 - controller if len(self.game_state.players) == 2 else controller

        from axis3.model.axis3_card import Axis3Card

        token_def = effect.token or {}
        types = token_def.get("types", ["Creature"])
        for _ in range(amount):
            card = Axis3Card(
                name=token_def.get("name", "Token"),
                mana_cost=None,
                mana_value=0,
                colors=token_def.get("colors", []),
                color_identity=token_def.get("colors", []),
                types=types,
                supertypes=[],
                subtypes=token_def.get("subtypes", []),
                power=token_def.get("power"),
                toughness=token_def.get("toughness"),
                loyalty=None,
                defense=None,
            )
            self.game_state.create_token(card, token_ctrl)
        return True

    def _scry(self, effect: a2.ScryEffect, source_id: str, controller: int) -> bool:
        player = self.game_state.players[controller]
        n = min(effect.amount, len(player.library))
        top = [player.library.pop() for _ in range(n)]
        # Default: keep order (bottom to top); real UI would reorder
        for card_id in reversed(top):
            player.library.insert(0, card_id)
        return True

    def _surveil(self, effect: a2.SurveilEffect, source_id: str, controller: int) -> bool:
        player = self.game_state.players[controller]
        n = min(effect.amount, len(player.library))
        for _ in range(n):
            if not player.library:
                break
            card_id = player.library.pop()
            self.game_state.zone_list(controller, "GRAVEYARD").append(card_id)
            obj = self.game_state.get_object(card_id)
            if obj:
                obj.zone = ZoneType.GRAVEYARD
        return True

    def _search(self, effect: a2.SearchEffect, source_id: str, controller: int) -> bool:
        zones = [z.upper() for z in (effect.zones or ["library"])]
        found = []
        for zone in zones:
            for oid in list(self.game_state.zone_list(controller, zone)):
                obj = self.game_state.get_object(oid)
                if obj and self._matches_search_filter(obj, effect.card_filter):
                    found.append(oid)
                    if effect.max_results and len(found) >= effect.max_results:
                        break
            if effect.max_results and len(found) >= effect.max_results:
                break

        dest = "BATTLEFIELD" if effect.put_onto_battlefield else "HAND"
        for oid in found:
            obj = self.game_state.get_object(oid)
            if not obj:
                continue
            from_z = obj.zone.name if hasattr(obj.zone, "name") else str(obj.zone)
            self._move_object(oid, from_z, dest, controller)

        if effect.shuffle_if_library_searched and "LIBRARY" in zones:
            random.shuffle(self.game_state.players[controller].library)
        return True

    def _shuffle(self, effect: a2.ShuffleEffect, source_id: str, controller: int) -> bool:
        for player in self.subjects.resolve(effect.subject, source_id, controller):
            if hasattr(player, "library"):
                random.shuffle(player.library)
        return True

    def _reveal(self, effect: a2.RevealEffect, source_id: str, controller: int) -> bool:
        self.game_state.add_debug_log(
            f"[Reveal] {effect.subject} (UI would show cards)"
        )
        return True

    def _transform(self, effect: a2.TransformEffect, source_id: str, controller: int) -> bool:
        for obj_id in self.subjects.resolve_object_ids(
            effect.subject, source_id, controller
        ):
            obj = self.game_state.get_object(obj_id)
            if obj and getattr(obj, "axis1_card", None):
                self.game_state.add_debug_log(f"[Transform] toggled face for {obj_id}")
        return True

    def _put_onto_battlefield(
        self, effect: a2.PutOntoBattlefieldEffect, source_id: str, controller: int
    ) -> bool:
        zone_from = (effect.zone_from or "graveyard").upper()
        for oid in list(self.game_state.zone_list(controller, zone_from)):
            obj = self.game_state.get_object(oid)
            if obj and self._matches_search_filter(obj, effect.card_filter):
                self._move_object(oid, zone_from, "BATTLEFIELD", controller, tapped=effect.tapped)
                if effect.max_results == 1:
                    break
        return True

    def _put_counter(self, effect: a2.PutCounterEffect, source_id: str, controller: int) -> bool:
        obj = self.game_state.get_object(source_id)
        if obj:
            obj.counters[effect.counter_type] = (
                obj.counters.get(effect.counter_type, 0) + effect.amount
            )
        return True

    def _add_counters(self, effect: a2.AddCountersEffect, source_id: str, controller: int) -> bool:
        count = resolve_amount(
            effect.count,
            game_state=self.game_state,
            source_id=source_id,
            controller=controller,
            default=1,
        )
        for obj_id in self.subjects.resolve_object_ids(
            effect.subject, source_id, controller
        ):
            obj = self.game_state.get_object(obj_id)
            if obj:
                obj.counters[effect.counter_type] = (
                    obj.counters.get(effect.counter_type, 0) + count
                )
        return True

    def _remove_counter(self, effect: a2.RemoveCounterEffect, source_id: str, controller: int) -> bool:
        subject = effect.subject
        obj_ids = (
            self.subjects.resolve_object_ids(subject, source_id, controller)
            if subject
            else [source_id]
        )
        for obj_id in obj_ids:
            obj = self.game_state.get_object(obj_id)
            if obj and effect.counter_type in obj.counters:
                obj.counters[effect.counter_type] = max(
                    0, obj.counters[effect.counter_type] - effect.amount
                )
        return True

    def _pt_boost(self, effect: a2.PTBoostEffect, source_id: str, controller: int) -> bool:
        from axis3.abilities.static import RuntimeContinuousEffect

        rce = RuntimeContinuousEffect(
            source_id=source_id,
            layer=7,
            sublayer="7b",
            applies_to=lambda gs, oid: oid == source_id,
            modify_power=lambda p: (p or 0) + effect.power,
            modify_toughness=lambda t: (t or 0) + effect.toughness,
        )
        self.game_state.continuous_effects.append(rce)
        return True

    def _gain_life_equal_power(
        self, effect: a2.GainLifeEqualToPowerEffect, source_id: str, controller: int
    ) -> bool:
        obj = self.game_state.get_object(source_id)
        amount = 0
        if obj and obj.axis2_card:
            power = obj.axis2_card.characteristics.power
            amount = resolve_amount(power, default=0)
        return self._gain_life(
            a2.GainLifeEffect(amount=amount, subject="you"),
            source_id,
            controller,
        )

    def _return_from_gy(
        self, effect: a2.ReturnCardFromGraveyardEffect, source_id: str, controller: int
    ) -> bool:
        dest = (effect.destination_zone or "hand").upper()
        for oid in list(self.game_state.zone_list(controller, "GRAVEYARD")):
            obj = self.game_state.get_object(oid)
            if not obj:
                continue
            if effect.subtype and effect.subtype not in (
                getattr(obj.axis2_card.characteristics, "subtypes", []) if obj.axis2_card else []
            ):
                continue
            self._move_object(oid, "GRAVEYARD", dest, controller)
        return True

    def _counter_spell(self, effect: a2.CounterSpellEffect, source_id: str, controller: int) -> bool:
        if self.game_state.stack.is_empty():
            return False
        top = self.game_state.stack.peek()
        if top:
            self.game_state.stack.pop()
        return True

    def _conditional(self, effect: a2.ConditionalEffect, source_id: str, controller: int) -> bool:
        # Without full condition DSL, execute nested effects when condition is informational
        if effect.condition in ("if_you_do", "exiled_this_way"):
            self.execute_all(effect.effects, source_id, controller)
            return True
        self.execute_all(effect.effects, source_id, controller)
        return True

    def _look_and_pick(self, effect: a2.LookAndPickEffect, source_id: str, controller: int) -> bool:
        zone = (effect.source_zone or "library").upper()
        player = self.game_state.players[controller]
        zone_list = self.game_state.zone_list(controller, zone)
        look_n = min(effect.look_at, len(zone_list))
        looked = [zone_list.pop() for _ in range(look_n)]
        if effect.put_rest_into == "graveyard":
            for cid in looked:
                self.game_state.zone_list(controller, "GRAVEYARD").append(cid)
        elif effect.put_rest_into == "bottom":
            for cid in reversed(looked):
                zone_list.insert(0, cid)
        return True

    def _mode(self, effect: a2.Mode, source_id: str, controller: int) -> bool:
        self.execute_all(effect.effects, source_id, controller)
        return True

    def _grant_casting_permission(
        self, effect: a2.GrantCastingPermissionEffect, source_id: str, controller: int
    ) -> bool:
        perm = f"cast_from_{effect.from_zone}"
        self.game_state.registries.permissions.grant(source_id, perm)
        return True

    def _register_static(self, effect: a2.StaticEffect, source_id: str, controller: int) -> bool:
        if not hasattr(self.game_state, "pending_static_effects"):
            self.game_state.pending_static_effects = []
        self.game_state.pending_static_effects.append((source_id, effect))
        return True

    def _register_replacement(
        self, effect: a2.ReplacementEffect, source_id: str, controller: int
    ) -> bool:
        if not hasattr(self.game_state, "pending_replacement_effects"):
            self.game_state.pending_replacement_effects = []
        self.game_state.pending_replacement_effects.append((source_id, effect))
        return True

    def _register_continuous(
        self, effect: a2.ContinuousEffect, source_id: str, controller: int
    ) -> bool:
        self.game_state.registries.continuous_effects.add((source_id, effect))
        return True

    def _equip(self, effect: a2.EquipEffect, source_id: str, controller: int) -> bool:
        self.game_state.add_debug_log("[Equip] requires targeting UI")
        return True

    def _cant_be_blocked(self, effect: a2.CantBeBlockedEffect, source_id: str, controller: int) -> bool:
        obj = self.game_state.get_object(source_id)
        if obj:
            if not hasattr(obj, "flags"):
                obj.flags = {}
            obj.flags["cant_be_blocked"] = True
        return True

    def _daybound(self, effect: a2.DayboundEffect, source_id: str, controller: int) -> bool:
        return True

    def _nightbound(self, effect: a2.NightboundEffect, source_id: str, controller: int) -> bool:
        return True

    def _draft_spellbook(
        self, effect: a2.DraftFromSpellbookEffect, source_id: str, controller: int
    ) -> bool:
        self.game_state.add_debug_log("[DraftFromSpellbook] not fully implemented")
        return True

    def _unparsed_oracle(
        self, effect: a2.UnparsedOracleEffect, source_id: str, controller: int
    ) -> bool:
        self.game_state.add_debug_log(
            f"[UnparsedOracle] kind={effect.heuristic_kind} hints={effect.hints}: "
            f"{effect.raw_text[:120]}"
        )
        return False

    def _lose_life(self, effect: a2.LoseLifeEffect, source_id: str, controller: int) -> bool:
        amount = resolve_amount(
            effect.amount,
            game_state=self.game_state,
            source_id=source_id,
            controller=controller,
            default=0,
        )
        if amount <= 0:
            return True
        subj = (effect.subject or "target_player").lower()
        if "each_opponent" in subj or "opponent" in subj:
            for pid, player in enumerate(self.game_state.players):
                if pid != controller:
                    atomic_life.apply_life_change(
                        self.game_state,
                        Event(
                            type=EventType.LIFE_CHANGE,
                            payload={"player_id": pid, "amount": -amount, "cause": source_id},
                        ),
                    )
        elif subj == "you":
            atomic_life.apply_life_change(
                self.game_state,
                Event(
                    type=EventType.LIFE_CHANGE,
                    payload={"player_id": controller, "amount": -amount, "cause": source_id},
                ),
            )
        else:
            atomic_life.apply_life_change(
                self.game_state,
                Event(
                    type=EventType.LIFE_CHANGE,
                    payload={"player_id": controller, "amount": -amount, "cause": source_id},
                ),
            )
        return True

    def _mill(self, effect: a2.MillEffect, source_id: str, controller: int) -> bool:
        amount = resolve_amount(
            effect.amount,
            game_state=self.game_state,
            source_id=source_id,
            controller=controller,
            default=1,
        )
        for player in self.subjects.resolve(effect.subject, source_id, controller):
            if not hasattr(player, "library"):
                continue
            pid = player.id
            for _ in range(amount):
                if not player.library:
                    break
                cid = player.library.pop()
                self.game_state.zone_list(pid, "GRAVEYARD").append(cid)
                obj = self.game_state.get_object(cid)
                if obj:
                    obj.zone = ZoneType.GRAVEYARD
        return True

    def _fight(self, effect: a2.FightEffect, source_id: str, controller: int) -> bool:
        self.game_state.add_debug_log("[Fight] combat module required")
        return True

    def _copy(self, effect: a2.CopyEffect, source_id: str, controller: int) -> bool:
        self.game_state.add_debug_log(f"[Copy] target={effect.target}")
        return True

    def _proliferate(self, effect: a2.ProliferateEffect, source_id: str, controller: int) -> bool:
        self.game_state.add_debug_log("[Proliferate] counter propagation required")
        return True

    def _venture(self, effect: a2.VentureEffect, source_id: str, controller: int) -> bool:
        self.game_state.add_debug_log(f"[Venture] {effect.action[:80]}")
        return True

    # ─────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────

    def _move_object(
        self,
        obj_id: str,
        from_zone: str,
        to_zone: Optional[str],
        controller: int,
        *,
        tapped: bool = False,
    ) -> None:
        try:
            self.game_state.move_card(obj_id, to_zone or "EXILE", controller=controller)
        except Exception:
            obj = self.game_state.get_object(obj_id)
            if not obj:
                return
            fz = from_zone.upper()
            if fz and obj_id in self.game_state.zone_list(controller, fz):
                self.game_state.zone_list(controller, fz).remove(obj_id)
            if to_zone:
                tz = to_zone.upper()
                self.game_state.zone_list(controller, tz).append(obj_id)
                obj.zone = getattr(ZoneType, tz, ZoneType.EXILE)
            else:
                del self.game_state.objects[obj_id]
                return
        obj = self.game_state.get_object(obj_id)
        if obj and tapped:
            obj.tapped = True

    def _matches_search_filter(self, obj: Any, card_filter: Optional[dict]) -> bool:
        if not card_filter:
            return True
        if not obj.axis2_card:
            return True
        chars = obj.axis2_card.characteristics
        if "types" in card_filter:
            needed = card_filter["types"]
            if not any(t in chars.types for t in needed):
                return False
        if "subtypes" in card_filter:
            needed = card_filter["subtypes"]
            if not any(s in chars.subtypes for s in needed):
                return False
        return True
