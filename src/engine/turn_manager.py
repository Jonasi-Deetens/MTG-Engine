from __future__ import annotations

from typing import List

from .ability_graph import AbilityGraphRuntimeAdapter
from .continuous import apply_continuous_effects
from .sba import apply_state_based_actions
from .events import Event
from .priority import PriorityManager
from .state import GameState, ResolveContext
from .turn import Phase, Step, PHASE_STEP_ORDER
from .zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD


class TurnManager:
    def __init__(self, game_state: GameState):
        self.gs = game_state
        self.state = self.gs.turn
        player_ids = [player.id for player in self.gs.players]
        self.priority = PriorityManager(player_order=player_ids)
        self._hydrate_priority()

    def _hydrate_priority(self) -> None:
        self.priority.current_index = self.state.priority_current_index
        self.priority.pass_count = self.state.priority_pass_count
        self.priority.last_passed_player = self.state.priority_last_passed_player_id

    def _persist_priority(self) -> None:
        self.state.priority_current_index = self.priority.current_index
        self.state.priority_pass_count = self.priority.pass_count
        self.state.priority_last_passed_player_id = self.priority.last_passed_player

    def begin_game(self) -> None:
        for player in self.gs.players:
            self._draw_cards(player.id, 7)
        self.state.turn_number = 1
        self.state.active_player_index = 0
        self._set_phase_step(Phase.BEGINNING, Step.UNTAP)
        self._begin_step()

    def handle_player_pass(self, player_id: int) -> None:
        if player_id != self.priority.current:
            return

        all_passed = self.priority.pass_priority()
        self._persist_priority()
        if not all_passed:
            return

        if self.gs.stack.is_empty():
            self._advance_phase_step()
            return

        resolved_item = self.gs.stack.pop()
        if resolved_item.kind == "spell":
            obj_id = resolved_item.payload.get("object_id")
            destination_zone = resolved_item.payload.get("destination_zone")
            obj = self.gs.objects.get(obj_id)
            context_data = resolved_item.payload.get("context") or {}
            context = ResolveContext(**context_data)
            from engine.targets import has_legal_targets, normalize_targets
            if obj:
                context.source_id = obj.id
                normalize_targets(self.gs, context)
                if not has_legal_targets(self.gs, context):
                    self.gs.move_object(obj.id, ZONE_GRAVEYARD)
                    obj.was_cast = False
                    self.gs.event_bus.publish(Event(
                        type="spell_fizzled",
                        payload={"object_id": obj.id, "controller_id": obj.controller_id},
                    ))
                    self.gs.log(f"Spell fizzles (illegal targets): {obj_id}")
                else:
                    if destination_zone:
                        resolved_destination = destination_zone
                    elif "Instant" in obj.types or "Sorcery" in obj.types:
                        resolved_destination = ZONE_GRAVEYARD
                    else:
                        resolved_destination = ZONE_BATTLEFIELD
                    if resolved_destination == ZONE_BATTLEFIELD:
                        enter_copy_of = context.choices.get("enter_copy_of")
                        if enter_copy_of:
                            self.gs._apply_enter_copy(obj, enter_copy_of)
                        enter_choices = context.choices.get("enter_choices")
                        if isinstance(enter_choices, dict):
                            self.gs._apply_enter_choices(obj, enter_choices)
                    self.gs.move_object(obj.id, resolved_destination)
                    obj.was_cast = False
                    self.gs.event_bus.publish(Event(
                        type="spell_resolved",
                        payload={"object_id": obj.id, "controller_id": obj.controller_id},
                    ))
                    self.gs.log(f"Resolved spell {obj_id}")
            else:
                self.gs.log(f"Resolved spell {obj_id}")
        elif resolved_item.kind == "ability_graph":
            payload = resolved_item.payload or {}
            graph = payload.get("graph")
            context_data = payload.get("context") or {}
            context = ResolveContext(**context_data)
            from engine.targets import normalize_targets, validate_targets
            from engine.choices import validate_enter_choices
            try:
                normalize_targets(self.gs, context)
                validate_targets(self.gs, context)
                adapter = AbilityGraphRuntimeAdapter(self.gs)
                if graph:
                    validate_enter_choices(graph, context.__dict__)
                    adapter.resolve(graph, context)
                source_id = payload.get("source_object_id")
                destination_zone = payload.get("destination_zone")
                if source_id and destination_zone:
                    obj = self.gs.objects.get(source_id)
                    if obj:
                        if destination_zone == ZONE_BATTLEFIELD:
                            enter_copy_of = context.choices.get("enter_copy_of")
                            if enter_copy_of:
                                self.gs._apply_enter_copy(obj, enter_copy_of)
                            enter_choices = context.choices.get("enter_choices")
                            if isinstance(enter_choices, dict):
                                self.gs._apply_enter_choices(obj, enter_choices)
                        self.gs.move_object(obj.id, destination_zone)
                        obj.was_cast = False
                if context.source_id:
                    self.gs.event_bus.publish(Event(
                        type="ability_resolved",
                        payload={"source_id": context.source_id, "controller_id": context.controller_id},
                    ))
                self.gs.log("Resolved ability graph")
            except ValueError as exc:
                self.gs.log(f"Ability fizzles: {exc}")
                source_id = payload.get("source_object_id")
                if source_id:
                    obj = self.gs.objects.get(source_id)
                    if obj:
                        self.gs.move_object(obj.id, ZONE_GRAVEYARD)
                        obj.was_cast = False
        else:
            self.gs.log(f"Resolved stack item {resolved_item.kind}")
        self.gs.clear_prepared_casts()
        apply_continuous_effects(self.gs)
        apply_state_based_actions(self.gs)
        self.priority.give_to(self.current_active_player_id())
        self._persist_priority()

    def after_player_action(self, player_id: int) -> None:
        if player_id != self.priority.current:
            return
        self.gs.clear_prepared_casts()
        apply_continuous_effects(self.gs)
        apply_state_based_actions(self.gs)
        self.priority.last_passed_player = None
        self.priority.pass_count = 0
        self._persist_priority()

    def after_mana_ability(self, player_id: int) -> None:
        if player_id != self.priority.current and player_id not in self.gs.prepared_casts:
            return
        apply_continuous_effects(self.gs)
        apply_state_based_actions(self.gs)
        self._persist_priority()

    def current_active_player_id(self) -> int:
        return self.gs.players[self.state.active_player_index].id

    def _set_phase_step(self, phase: Phase, step: Step) -> None:
        self.state.phase = phase
        self.state.step = step

    def _begin_step(self) -> None:
        self.gs.event_bus.publish(Event(
            type="begin_step",
            payload={
                "phase": self.state.phase,
                "step": self.state.step,
                "active_player": self.current_active_player_id(),
                "turn_number": self.state.turn_number,
            }
        ))
        self._reset_activation_limits("phase")
        if self.state.step == Step.UPKEEP:
            self._expire_temporary_effects(self.state.step)
        if self.state.step == Step.UPKEEP:
            self.gs.event_bus.publish(Event(type="upkeep", payload={"player_id": self.current_active_player_id()}))
        if self.state.step == Step.BEGIN_COMBAT:
            self._reset_activation_limits("combat")
        if self.state.step == Step.DRAW:
            self.gs.event_bus.publish(Event(type="draw_step", payload={"player_id": self.current_active_player_id()}))
        if self.state.step == Step.END:
            self.gs.event_bus.publish(Event(type="end_step", payload={"player_id": self.current_active_player_id()}))
        apply_continuous_effects(self.gs)
        apply_state_based_actions(self.gs)
        self.priority.reset_for_new_step(self.current_active_player_id())
        self._persist_priority()

        if self.state.step == Step.UNTAP:
            self._handle_untap_step()
            self._advance_phase_step()
            return
        if self.state.step == Step.DRAW:
            self._handle_draw_step()
            self.priority.reset_for_new_step(self.current_active_player_id())
            return
        if self.state.step == Step.COMBAT_DAMAGE:
            self._handle_combat_damage_step()
            self.priority.reset_for_new_step(self.current_active_player_id())
            return
        if self.state.step == Step.CLEANUP:
            self._handle_cleanup_step()
            self._advance_phase_step()
            return

    def _end_step(self) -> None:
        self.gs.event_bus.publish(Event(
            type="end_step",
            payload={
                "phase": self.state.phase,
                "step": self.state.step,
                "active_player": self.current_active_player_id(),
                "turn_number": self.state.turn_number,
            }
        ))
        if self.state.step in (Step.END_COMBAT, Step.CLEANUP):
            self._expire_temporary_effects(self.state.step)
        for player in self.gs.players:
            player.mana_pool = {}
        self.gs.replacement_effects = []

    def _advance_phase_step(self) -> None:
        current_pair = (self.state.phase, self.state.step)
        idx = PHASE_STEP_ORDER.index(current_pair)
        self._end_step()

        if idx == len(PHASE_STEP_ORDER) - 1:
            self._start_next_turn()
            return
        next_phase, next_step = PHASE_STEP_ORDER[idx + 1]
        self._set_phase_step(next_phase, next_step)
        self._begin_step()

    def _start_next_turn(self) -> None:
        self.state.turn_number += 1
        self.state.active_player_index = (self.state.active_player_index + 1) % len(self.gs.players)
        self.state.land_plays_this_turn = 0
        self.state.combat_state = None
        self._reset_activation_limits("turn")
        first_phase, first_step = PHASE_STEP_ORDER[0]
        self._set_phase_step(first_phase, first_step)
        self._begin_step()

    def _handle_untap_step(self) -> None:
        active_player_id = self.current_active_player_id()
        self.gs.event_bus.publish(Event(
            type="untap",
            payload={"active_player": active_player_id}
        ))
        for obj_id in self.gs.get_player(active_player_id).battlefield:
            obj = self.gs.objects.get(obj_id)
            if obj:
                if obj.phased_out:
                    obj.phased_out = False
                    continue
                obj.tapped = False

    def _handle_draw_step(self) -> None:
        active_player_id = self.current_active_player_id()
        self._draw_cards(active_player_id, 1)

    def _handle_combat_damage_step(self) -> None:
        self.gs.event_bus.publish(Event(
            type="combat_damage",
            payload={"active_player": self.current_active_player_id()}
        ))

    def _handle_cleanup_step(self) -> None:
        for obj in self.gs.objects.values():
            if obj.zone == ZONE_BATTLEFIELD:
                obj.damage = 0
                obj.is_attacking = False
                obj.is_blocking = False
        self.state.combat_state = None

    def _expire_temporary_effects(self, step: Step) -> None:
        active_player_id = self.current_active_player_id()
        for obj in self.gs.objects.values():
            if not obj.temporary_effects:
                continue
            remaining = []
            for effect in obj.temporary_effects:
                duration = effect.get("duration")
                controller_id = effect.get("controller_id")
                if duration == "until_end_of_combat" and step == Step.END_COMBAT:
                    if effect.get("type") == "set_controller" and effect.get("original_controller") is not None:
                        obj.controller_id = effect.get("original_controller")
                    continue
                if duration == "until_end_of_turn" and step == Step.CLEANUP:
                    if effect.get("type") == "set_controller" and effect.get("original_controller") is not None:
                        obj.controller_id = effect.get("original_controller")
                    continue
                if duration == "until_end_of_your_next_turn" and step == Step.CLEANUP:
                    if controller_id == active_player_id:
                        if effect.get("type") == "set_controller" and effect.get("original_controller") is not None:
                            obj.controller_id = effect.get("original_controller")
                        continue
                if duration == "until_your_next_upkeep" and step == Step.UPKEEP:
                    if controller_id == active_player_id:
                        if effect.get("type") == "set_controller" and effect.get("original_controller") is not None:
                            obj.controller_id = effect.get("original_controller")
                        continue
                if duration is None and "prevent_damage" in effect and step == Step.CLEANUP:
                    continue
                remaining.append(effect)
            obj.temporary_effects = remaining

    def _draw_cards(self, player_id: int, count: int) -> None:
        player = self.gs.get_player(player_id)
        for _ in range(count):
            if not player.library:
                return
            card_id = player.library.pop(0)
            player.hand.append(card_id)

    def _reset_activation_limits(self, scope: str) -> None:
        for obj in self.gs.objects.values():
            if not obj.activation_limits:
                continue
            to_remove = [key for key in obj.activation_limits if key.endswith(f":{scope}")]
            for key in to_remove:
                obj.activation_limits.pop(key, None)
