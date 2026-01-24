from __future__ import annotations

from typing import List, Optional
import os

from .continuous import apply_continuous_effects
from .sba import apply_state_based_actions
from .events import Event
from .priority import PriorityManager
from .replacements import resolve_replacement
from .stack import StackItem
from .stack_resolution.stack_resolver import StackResolver
from .state import GameState, ResolveContext
from .turn import Phase, Step, PHASE_STEP_ORDER
from .turn_handling.phase_handler import PhaseHandler
from .zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD, ZONE_HAND


class TurnManager:
    """Manages turn structure, priority, and phase/step transitions.

    Delegates:
    - Stack resolution to StackResolver
    - Phase/step handling to PhaseHandler
    """

    def __init__(self, game_state: GameState):
        self.gs = game_state
        self.state = self.gs.turn
        player_ids = self._alive_player_ids()
        self.priority = PriorityManager(player_order=player_ids)
        self._stack_resolver = StackResolver(game_state)
        self._phase_handler = PhaseHandler(game_state, self.current_active_player_id)
        self._hydrate_priority()

    @property
    def stack_resolver(self) -> StackResolver:
        """Get the StackResolver."""
        return self._stack_resolver

    @property
    def phase_handler(self) -> PhaseHandler:
        """Get the PhaseHandler."""
        return self._phase_handler

    def _hydrate_priority(self) -> None:
        self.priority.current_index = self.state.priority_current_index
        self.priority.pass_count = self.state.priority_pass_count
        self.priority.last_passed_player = self.state.priority_last_passed_player_id

    def _persist_priority(self) -> None:
        self.state.priority_current_index = self.priority.current_index
        self.state.priority_pass_count = self.priority.pass_count
        self.state.priority_last_passed_player_id = self.priority.last_passed_player

    def _alive_player_ids(self) -> List[int]:
        return [player.id for player in self.gs.players if not getattr(player, "has_lost", False)]

    def _next_active_index(self, start_index: int) -> int:
        total = len(self.gs.players)
        if total == 0:
            return start_index
        for offset in range(1, total + 1):
            idx = (start_index + offset) % total
            if not getattr(self.gs.players[idx], "has_lost", False):
                return idx
        return start_index

    def _ensure_active_player(self) -> None:
        if not self.gs.players:
            return
        current = self.gs.players[self.state.active_player_index]
        if getattr(current, "has_lost", False):
            self.state.active_player_index = self._next_active_index(self.state.active_player_index)

    def _sync_priority(self, current_player_id: Optional[int] = None, preserve_pass_state: bool = False) -> None:
        alive_ids = self._alive_player_ids()
        if not alive_ids:
            return
        self._place_pending_triggers()
        if current_player_id is None:
            current_player_id = alive_ids[0]
        saved_pass_state = None
        if preserve_pass_state and alive_ids == self.priority.player_order:
            saved_pass_state = (self.priority.pass_count, self.priority.last_passed_player)
        self.priority.update_order(alive_ids, current_player_id)
        if saved_pass_state:
            self.priority.pass_count, self.priority.last_passed_player = saved_pass_state
        self._persist_priority()

    def _place_pending_triggers(self) -> bool:
        if not self.gs.pending_triggers:
            return False
        for entry in list(self.gs.pending_triggers):
            self.gs.stack.push(StackItem(
                kind=entry.get("kind", "effect_graph"),
                payload=entry.get("payload", {}),
                controller_id=entry.get("controller_id"),
            ))
        self.gs.pending_triggers.clear()
        return True

    def begin_game(self) -> None:
        for player in self.gs.players:
            self._draw_cards(player.id, 7)
        self.state.turn_number = 1
        self.state.active_player_index = 0
        self._ensure_active_player()
        self._set_phase_step(Phase.BEGINNING, Step.UNTAP)
        self._begin_step()

    def handle_player_pass(self, player_id: int, provided_context: dict = None) -> dict:
        """Handle a player passing priority.
        
        Args:
            player_id: The player passing priority
            provided_context: Optional context with choices like search_results
        
        Returns:
            Dict with status and any pending choices needed
        """
        self._sync_priority(self.priority.current, preserve_pass_state=True)
        if player_id != self.priority.current:
            return {"status": "not_your_priority"}
        if self.state.step == Step.DECLARE_ATTACKERS:
            combat_state = self.state.combat_state
            if not combat_state or not combat_state.attackers_declared:
                return {"status": "attackers_not_declared"}
        if self.state.step == Step.DECLARE_BLOCKERS:
            combat_state = self.state.combat_state
            if not combat_state or not combat_state.blockers_declared:
                return {"status": "blockers_not_declared"}

        # Store any provided selections BEFORE checking all_passed
        # This ensures selections are saved even when passing priority early
        if provided_context and "targets_by_effect" in provided_context:
            for node_id, targets in provided_context["targets_by_effect"].items():
                if node_id not in self.gs.pending_search_selections:
                    self.gs.pending_search_selections[node_id] = {}
                # Merge in the new selections
                for key, value in targets.items():
                    if key == "search_results_by_player" and isinstance(value, dict):
                        if "search_results_by_player" not in self.gs.pending_search_selections[node_id]:
                            self.gs.pending_search_selections[node_id]["search_results_by_player"] = {}
                        self.gs.pending_search_selections[node_id]["search_results_by_player"].update(value)
                    else:
                        self.gs.pending_search_selections[node_id][key] = value
            print(f"[graph] stored pending_search_selections: {self.gs.pending_search_selections}", flush=True)

        all_passed = self.priority.pass_priority()
        self._persist_priority()
        print(f"[graph] handle_player_pass: all_passed={all_passed}", flush=True)
        if not all_passed:
            return {"status": "passed"}
        
        pending_count = len(self.gs.pending_triggers)
        print(f"[graph] handle_player_pass: checking pending_triggers count={pending_count}", flush=True)
        if self._place_pending_triggers():
            self._sync_priority(self.current_active_player_id())
            print(f"[graph] handle_player_pass: triggers placed, stack_size={len(self.gs.stack.items)}", flush=True)
            return {"status": "triggers_placed"}

        if self.gs.stack.is_empty():
            self._advance_phase_step()
            return {"status": "phase_advanced"}

        print(f"[graph] handle_player_pass: calling resolve_top, stack_size={len(self.gs.stack.items)}", flush=True)
        
        # Build combined context from stored selections and provided context
        combined_context = {"targets_by_effect": dict(self.gs.pending_search_selections)}
        if provided_context and "targets_by_effect" in provided_context:
            for node_id, targets in provided_context["targets_by_effect"].items():
                if node_id not in combined_context["targets_by_effect"]:
                    combined_context["targets_by_effect"][node_id] = {}
                combined_context["targets_by_effect"][node_id].update(targets)
        
        print(f"[graph] combined_context for resolve_top: {combined_context}", flush=True)
        
        # Delegate stack resolution to StackResolver
        result = self._stack_resolver.resolve_top(combined_context if combined_context["targets_by_effect"] else None)
        
        # Check if input is needed before resolution can proceed
        if result and result.needs_input:
            # Reset pass state and give priority to the player who needs to make the choice
            self.priority._pass_count = 0
            # Find the first player who needs to make a choice and give them priority
            if result.pending_search_choices:
                choice_player = result.pending_search_choices[0].player_id
                print(f"[graph] needs_input: giving priority to player {choice_player}", flush=True)
                self._sync_priority(choice_player)
            self._persist_priority()
            print(f"[graph] needs_input: priority_current_index={self.state.priority_current_index}", flush=True)
            return {
                "status": "needs_input",
                "pending_search_choices": [
                    {
                        "node_id": choice.node_id,
                        "player_id": choice.player_id,
                        "zone": choice.zone,
                        "options": choice.options,
                        "min_selections": choice.min_selections,
                        "max_selections": choice.max_selections,
                        "source_id": choice.source_id,
                    }
                    for choice in result.pending_search_choices
                ],
            }
        
        # Clear pending search selections after successful resolution
        self.gs.pending_search_selections.clear()
        
        print(f"[graph] handle_player_pass: resolved, stack_size_after={len(self.gs.stack.items)}", flush=True)
        
        self.gs.clear_prepared_casts()
        apply_continuous_effects(self.gs)
        apply_state_based_actions(self.gs)
        self._ensure_active_player()
        if self._place_pending_triggers():
            self._sync_priority(self.current_active_player_id())
            return {"status": "triggers_placed"}
        self._sync_priority(self.current_active_player_id())
        return {"status": "resolved"}

    def after_player_action(self, player_id: int) -> None:
        if player_id != self.priority.current:
            return
        self.gs.clear_prepared_casts()
        apply_continuous_effects(self.gs)
        apply_state_based_actions(self.gs)
        self._ensure_active_player()
        current_id = self.priority.current if self.priority.current in self._alive_player_ids() else self.current_active_player_id()
        self._sync_priority(current_id)

    def after_mana_ability(self, player_id: int) -> None:
        if player_id != self.priority.current and player_id not in self.gs.prepared_casts:
            return
        apply_continuous_effects(self.gs)
        apply_state_based_actions(self.gs)
        self._ensure_active_player()
        current_id = self.priority.current if self.priority.current in self._alive_player_ids() else self.current_active_player_id()
        self._sync_priority(current_id)

    def current_active_player_id(self) -> int:
        self._ensure_active_player()
        return self.gs.players[self.state.active_player_index].id

    def _set_phase_step(self, phase: Phase, step: Step) -> None:
        self.state.phase = phase
        self.state.step = step

    def _begin_step(self) -> None:
        if os.getenv("ENGINE_TRACE") == "1":
            print(
                f"[engine] begin_step t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
                flush=True,
            )
        self._ensure_active_player()
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
        print("[engine] apply_continuous_effects start", flush=True)
        apply_continuous_effects(self.gs)
        print("[engine] apply_continuous_effects end", flush=True)
        print("[engine] apply_state_based_actions start", flush=True)
        apply_state_based_actions(self.gs)
        print("[engine] apply_state_based_actions end", flush=True)
        self._ensure_active_player()
        self._sync_priority(self.current_active_player_id())

        if self.state.step == Step.UNTAP:
            self._handle_untap_step()
            self._advance_phase_step()
            return
        if self.state.step == Step.DRAW:
            self._handle_draw_step()
            self._ensure_active_player()
            self._sync_priority(self.current_active_player_id())
            return
        if self.state.step == Step.COMBAT_DAMAGE:
            self._handle_combat_damage_step()
            self._ensure_active_player()
            self._sync_priority(self.current_active_player_id())
            return
        if self.state.step == Step.CLEANUP:
            print("[engine] cleanup_step handler start", flush=True)
            self._handle_cleanup_step()
            print("[engine] cleanup_step handler end", flush=True)
            self._advance_phase_step()
            return

    def _end_step(self) -> None:
        if os.getenv("ENGINE_TRACE") == "1":
            print(
                f"[engine] end_step t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
                flush=True,
            )
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
        if self.state.step == Step.END_COMBAT:
            for obj in self.gs.objects.values():
                if obj.zone == ZONE_BATTLEFIELD:
                    obj.is_attacking = False
                    obj.is_blocking = False
            self.state.combat_state = None
        for player in self.gs.players:
            player.mana_pool = {}
        self.gs.replacement_effects = []

    def _advance_phase_step(self) -> None:
        if os.getenv("ENGINE_TRACE") == "1":
            print(
                f"[engine] advance_step start t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
                flush=True,
            )
        print(
            f"[engine] advance_step start t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
            flush=True,
        )
        current_pair = (self.state.phase, self.state.step)
        idx = PHASE_STEP_ORDER.index(current_pair)
        self._end_step()
        print("[engine] advance_step after end_step", flush=True)

        if idx == len(PHASE_STEP_ORDER) - 1:
            self._start_next_turn()
            if os.getenv("ENGINE_TRACE") == "1":
                print(
                    f"[engine] advance_step end t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
                    flush=True,
                )
            print(
                f"[engine] advance_step end t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
                flush=True,
            )
            return
        next_phase, next_step = PHASE_STEP_ORDER[idx + 1]
        self._set_phase_step(next_phase, next_step)
        print(
            f"[engine] advance_step next t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
            flush=True,
        )
        self._begin_step()
        if os.getenv("ENGINE_TRACE") == "1":
            print(
                f"[engine] advance_step end t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
                flush=True,
            )
        print(
            f"[engine] advance_step end t{self.state.turn_number} {self.state.phase.value}:{self.state.step.value}",
            flush=True,
        )

    def _start_next_turn(self) -> None:
        self.state.turn_number += 1
        self.state.active_player_index = self._next_active_index(self.state.active_player_index)
        self.state.land_plays_this_turn = 0
        self.state.combat_state = None
        self._reset_activation_limits("turn")
        first_phase, first_step = PHASE_STEP_ORDER[0]
        self._set_phase_step(first_phase, first_step)
        self._begin_step()

    def _handle_untap_step(self) -> None:
        """Handle the untap step. Delegates to PhaseHandler."""
        self._phase_handler.handle_untap()

    def _handle_draw_step(self) -> None:
        """Handle the draw step. Delegates to PhaseHandler."""
        self._phase_handler.handle_draw()

    def _handle_combat_damage_step(self) -> None:
        """Handle the combat damage step. Delegates to PhaseHandler."""
        self._phase_handler.handle_combat_damage()

    def _handle_cleanup_step(self) -> None:
        """Handle the cleanup step. Delegates to PhaseHandler."""
        self._phase_handler.handle_cleanup()

    def _discard_to_hand_size(self, player) -> None:
        """Discard to hand size. Delegates to PhaseHandler."""
        self._phase_handler.discard_to_hand_size(player)

    def _expire_temporary_effects(self, step: Step) -> None:
        """Expire temporary effects. Delegates to PhaseHandler."""
        self._phase_handler.expire_temporary_effects(step)

    def _draw_cards(self, player_id: int, count: int) -> None:
        """Draw cards. Delegates to PhaseHandler."""
        self._phase_handler.draw_cards(player_id, count)

    def _reset_activation_limits(self, scope: str) -> None:
        """Reset activation limits. Delegates to PhaseHandler."""
        self._phase_handler.reset_activation_limits(scope)
