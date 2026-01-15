from __future__ import annotations

from typing import List

from .events import Event
from .priority import PriorityManager
from .state import GameState
from .turn import Phase, Step, PHASE_STEP_ORDER
from .zones import ZONE_BATTLEFIELD


class TurnManager:
    def __init__(self, game_state: GameState):
        self.gs = game_state
        self.state = self.gs.turn
        player_ids = [player.id for player in self.gs.players]
        self.priority = PriorityManager(player_order=player_ids)

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
        if not all_passed:
            return

        if self.gs.stack.is_empty():
            self._advance_phase_step()
            return

        resolved_item = self.gs.stack.pop()
        self.gs.log(f"Resolved stack item {resolved_item.kind}")
        self.priority.give_to(self.current_active_player_id())

    def after_player_action(self, player_id: int) -> None:
        if player_id != self.priority.current:
            return
        self.priority.current_index = (self.priority.current_index + 1) % len(self.priority.player_order)
        self.priority.last_passed_player = None
        self.priority.pass_count = 0

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
        self.priority.reset_for_new_step(self.current_active_player_id())

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

    def _draw_cards(self, player_id: int, count: int) -> None:
        player = self.gs.get_player(player_id)
        for _ in range(count):
            if not player.library:
                return
            card_id = player.library.pop(0)
            player.hand.append(card_id)
