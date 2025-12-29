from __future__ import annotations
from dataclasses import dataclass

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.rules.sba.checker import run_sbas
from axis3.state.zones import ZoneType
from axis3.state.game_state import Phase

from .steps import Step, PHASE_STEP_ORDER
from .priority import PriorityManager


class TurnManager:
    """
    Central coordinator for turn/step/priority flow.

    Design goals:
    - Correct MTG turn/priority structure.
    - UI-agnostic (no input/output).
    - Rules-light: delegates real rules work via events and hooks.
    """

    def __init__(self, game_state: "GameState"):
        self.gs = game_state
        # Use the canonical TurnState stored in GameState
        self.state = self.gs.turn
        self.priority = PriorityManager(active_player=self.state.active_player)


    # --- Public API ---------------------------------------------------------

    def begin_game(self):
        """
        Initialize the first turn: set phase/step, handle automatic actions,
        and give priority at the first step that actually has priority.
        """
        self.state.turn_number = 1
        self.state.active_player = 0
        self._set_phase_step(Phase.BEGINNING, Step.UNTAP)
        self._begin_step()

    def handle_player_pass(self, player_id: int):
        """
        Called by the engine loop/UI when the current priority player passes.
        This may cause stack resolution or step advancement.
        """
        if player_id != self.priority.current:
            return  # Ignore out-of-turn passes

        both_passed = self.priority.pass_priority()
        if not both_passed:
            return

        # Both players passed in succession
        if self.gs.stack.is_empty():
            # Advance step/phase/turn
            self._advance_phase_step()
        else:
            # Resolve top of stack, run SBAs, give priority back to active player
            self.gs.stack.resolve_top(self.gs)
            run_sbas(self.gs)
            self.priority.give_to(self.state.active_player)

    def after_player_action(self, player_id: int):
        """
        Called after a player successfully takes an action that uses priority
        (cast spell, activate ability, etc.). We give priority to the other player.
        """
        if player_id != self.priority.current:
            return

        # After an action, priority passes to the other player
        self.priority.priority_player ^= 1
        self.priority._last_passed_player = None

    # --- Internal phase/step management ------------------------------------

    def _set_phase_step(self, phase: Phase, step: Step):
        self.state.phase = phase
        self.state.step = step

    def _begin_step(self):
        """
        Handle the beginning of a step:
        - publish BEGIN_STEP event
        - run automatic step actions where appropriate
        - run SBAs
        - either:
            * give priority (most steps), or
            * auto-advance (UNTAP, some CLEANUP cases)
        """
        self.gs.event_bus.publish(Event(
            type=EventType.BEGIN_STEP,
            payload={
                "phase": self.state.phase,
                "step": self.state.step,
                "active_player": self.state.active_player,
                "turn_number": self.state.turn_number,
            }
        ))

        step = self.state.step

        # --- Automatic, no-priority steps: UNTAP, some parts of CLEANUP -----
        if step == Step.UNTAP:
            self._handle_untap_step()
            # No priority in untap; go straight to next step
            self._advance_phase_step()
            return

        # --- Automatic actions but with priority afterwards -----------------
        if step == Step.DRAW:
            self._handle_draw_step()
            run_sbas(self.gs)
            self.priority.reset_for_new_step(self.state.active_player)
            return

        if step == Step.COMBAT_DAMAGE:
            self._handle_combat_damage_step()
            run_sbas(self.gs)
            # Players do get priority after combat damage
            self.priority.reset_for_new_step(self.state.active_player)
            return

        # --- Cleanup: automatic, but can loop if SBAs/Triggers occur -------
        if step == Step.CLEANUP:
            if self._handle_cleanup_step():
                # If state-based actions or triggers require another cleanup,
                # we stay in cleanup. Rules layer should manage that via events.
                return
            # Normally, cleanup has no priority; move to next turn
            self._advance_phase_step()
            return

        # --- All other steps: just give priority after BEGIN_STEP ----------
        run_sbas(self.gs)
        self.priority.reset_for_new_step(self.state.active_player)

    def _end_step(self):
        """
        Fire END_STEP event.
        """
        self.gs.event_bus.publish(Event(
            type=EventType.END_STEP,
            payload={
                "phase": self.state.phase,
                "step": self.state.step,
                "active_player": self.state.active_player,
                "turn_number": self.state.turn_number,
            }
        ))

    def _advance_phase_step(self):
        """
        Advance to the next (phase, step) pair in PHASE_STEP_ORDER.
        If we loop back to the beginning, advance turn and active player.
        """
        current_pair = (self.state.phase, self.state.step)
        idx = PHASE_STEP_ORDER.index(current_pair)

        self._end_step()

        if idx == len(PHASE_STEP_ORDER) - 1:
            # End of turn → new turn
            self._start_next_turn()
        else:
            next_phase, next_step = PHASE_STEP_ORDER[idx + 1]
            self._set_phase_step(next_phase, next_step)
            self._begin_step()

    def _start_next_turn(self):
        """
        Increment turn, switch active player, and go to the first step.
        """
        self.state.turn_number += 1
        self.state.active_player ^= 1  # two-player game assumption
        self.state.lands_played_this_turn = {0: 0, 1: 0}

        first_phase, first_step = PHASE_STEP_ORDER[0]
        self._set_phase_step(first_phase, first_step)
        self._begin_step()

    # --- Step-specific handlers (hooks into rules layer) -------------------

    def _handle_untap_step(self):
        """
        Untap step:
        - No priority.
        - Active player's permanents untap.
        - SBAs and triggered abilities are handled via events/other rules.
        """
        self.gs.event_bus.publish(Event(
            type=EventType.UNTAP,
            payload={"active_player": self.state.active_player}
        ))
        # You can keep this as events-only and let rules layer untap

    def _handle_draw_step(self):
        player = self.gs.players[self.state.active_player]

        # 1. Fire DRAW (replacement window)
        self.gs.event_bus.publish(Event(
            type=EventType.DRAW,
            payload={"player_id": player.id}
        ))


    def _handle_combat_damage_step(self):
        """
        Combat damage step:
        - Deal combat damage according to the combat state.
        - Then players get priority.
        Real logic should live in the combat/rules layer; here we just emit events.
        """
        self.gs.event_bus.publish(Event(
            type=EventType.COMBAT_DAMAGE,
            payload={
                "active_player": self.state.active_player,
                "turn_number": self.state.turn_number,
            }
        ))
        # Actual damage assignment/resolution should be in axis3.engine.combat
        # called by a subscriber to COMBAT_DAMAGE_STEP.

    def _handle_cleanup_step(self) -> bool:
        """
        Cleanup step:
        - Discard down to max hand size.
        - Remove damage from creatures.
        - Effects that last 'until end of turn' are cleared in the rules layer.
        - Normally, no priority. But if SBAs or triggers cause changes,
          an additional cleanup is performed.

        Returns:
            True if an additional cleanup is required (rules layer decides),
            False otherwise.
        """
        self.gs.event_bus.publish(Event(
            type=EventType.BEGIN_STEP,
            payload={
                "active_player": self.state.active_player,
                "turn_number": self.state.turn_number,
            }
        ))

        # Example: simple damage removal here; real logic may live elsewhere.
        for obj in self.gs.objects.values():
            if obj.zone.name == "BATTLEFIELD":
                obj.damage = 0

        run_sbas(self.gs)

        # In a full engine, this would be coordinated with the rules layer:
        # if any triggers fired or SBAs caused changes that require another
        # cleanup, return True. For now, we assume no extra cleanup.
        return False

    # --- Convenience accessors for UI/engine loop --------------------------

    @property
    def active_player(self) -> int:
        return self.state.active_player

    @property
    def priority_player(self) -> int:
        return self.priority.current

    @property
    def phase(self) -> Phase:
        return self.state.phase

    @property
    def step(self) -> Step:
        return self.state.step
