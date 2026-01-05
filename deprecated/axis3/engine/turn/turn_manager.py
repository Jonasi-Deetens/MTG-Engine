# axis3/engine/turn/turn_manager.py

from __future__ import annotations
from typing import TYPE_CHECKING

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.engine.turn.priority import PriorityManager
from axis3.rules.sba.checker import run_sbas
from axis3.engine.turn.turn_state import Phase, Step, PHASE_STEP_ORDER

if TYPE_CHECKING:
    from axis3.state.game_state import GameState


class TurnManager:
    """
    Central coordinator for turn/step/priority/stack flow.

    Design goals:
    - Correct MTG turn/priority structure.
    - UI-agnostic (no input/output).
    - Rules-light: delegates real rules work via events, engines, and handlers.
    """

    def __init__(self, game_state: GameState):
        self.gs = game_state
        # Use the canonical TurnState stored in GameState
        self.state = self.gs.turn
        self.priority = PriorityManager(active_player=self.state.active_player)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _draw_cards(self, player_id: int, count: int):
        """
        Draw `count` cards for `player_id` via the normal DRAW event pipeline
        (replacement effects, triggers, etc.).
        """
        self.gs.add_debug_log(f"TurnManager: drawing {count} cards for player {player_id}")
        for _ in range(count):
            self.gs.event_bus.publish(Event(
                type=EventType.DRAW,
                payload={"player_id": player_id}
            ))
            # Draw implementation lives in rules handlers.

    def _set_phase_step(self, phase: Phase, step: Step):
        self.state.phase = phase
        self.state.step = step

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def begin_game(self):
        """
        Initialize the first turn:
        - draw starting hands
        - set first turn/phase/step
        - begin the first step
        """
        # Starting hands
        for pid, player in enumerate(self.gs.players):
            self._draw_cards(player.id, 7)

        self.state.turn_number = 1
        self.state.active_player = 0
        self._set_phase_step(Phase.BEGINNING, Step.UNTAP)
        self._begin_step()

    def handle_player_pass(self, player_id: int):
        """
        Called by the engine loop/UI when the current priority player passes.

        If both players have passed in succession:
        - If the stack is non-empty, resolve the top item, run SBAs, and give
          priority back to the active player.
        - If the stack is empty, advance phase/step/turn.
        """
        if player_id != self.priority.current:
            return  # Ignore out-of-turn passes

        both_passed = self.priority.pass_priority()
        if not both_passed:
            return

        # Both players passed in succession
        if self.gs.stack.is_empty():
            # No spells/abilities to resolve → advance game state
            self._advance_phase_step()
        else:
            # Resolve top of stack, run SBAs, give priority back to active player
            resolved_item = self.gs.stack.resolve_top(self.gs)
            self.gs.add_debug_log(
                f"TurnManager: resolved stack item {resolved_item}"
            )
            run_sbas(self.gs)
            # After a stack item resolves, active player gets priority first
            self.priority.give_to(self.state.active_player)

    def after_player_action(self, player_id: int):
        """
        Called AFTER a player successfully takes an action that USES PRIORITY
        (cast spell, activate ability, etc.).

        Mana abilities and special actions that don't use the stack must NOT
        call this; the action object should expose `uses_priority`.
        """
        if player_id != self.priority.current:
            return

        # After an action that uses the stack, priority goes to the other player
        self.priority.priority_player ^= 1
        self.priority._last_passed_player = None

    # -------------------------------------------------------------------------
    # Phase/step management
    # -------------------------------------------------------------------------

    def _begin_step(self):
        """
        Handle the beginning of a step:

        - publish BEGIN_STEP event
        - allow triggered abilities to be created/queued
        - run automatic step actions where appropriate
        - run SBAs
        - either:
            * give priority (most steps), or
            * auto-advance (UNTAP, some CLEANUP cases)
        """

        # BEGIN_STEP event: triggers like "At the beginning of your upkeep..."
        self.gs.event_bus.publish(Event(
            type=EventType.BEGIN_STEP,
            payload={
                "phase": self.state.phase,
                "step": self.state.step,
                "active_player": self.state.active_player,
                "turn_number": self.state.turn_number,
            }
        ))

        # Default: active player starts with priority each step (unless overridden below)
        self.priority.give_to(self.state.active_player)

        step = self.state.step

        # --- Automatic, no-priority steps: UNTAP -----------------------------
        if step == Step.UNTAP:
            self._handle_untap_step()
            # If UNTAP produced triggers (e.g., "Whenever this untaps"), they go on the stack.
            # MTG: no priority in untap; we still must handle triggers via events.
            # By rules, those triggers actually wait until the next step's priority.
            # So we go straight to the next step.
            self._advance_phase_step()
            return

        # --- DRAW step: automatic draw, THEN priority ------------------------
        if step == Step.DRAW:
            self._handle_draw_step()
            run_sbas(self.gs)

            # If the draw step (or its triggers) put items on the stack,
            # we now enter a normal priority window.
            self.priority.reset_for_new_step(self.state.active_player)
            return

        # --- COMBAT DAMAGE: automatic damage, THEN priority ------------------
        if step == Step.COMBAT_DAMAGE:
            self._handle_combat_damage_step()
            run_sbas(self.gs)
            self.priority.reset_for_new_step(self.state.active_player)
            return

        # --- CLEANUP: automatic, but can loop if SBAs/Triggers occur --------
        if step == Step.CLEANUP:
            if self._handle_cleanup_step():
                # If the rules layer determined another cleanup is required,
                # remain in CLEANUP. Rules layer manages any needed events.
                return
            # Normally, cleanup has no priority; move to next turn
            self._advance_phase_step()
            return

        # --- All other steps: normal priority window ------------------------
        # BEGIN_STEP already fired; any triggers have had a chance to go on stack.
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
        self.state.active_player ^= 1  # two-player assumption
        self.state.lands_played_this_turn = {0: 0, 1: 0}

        first_phase, first_step = PHASE_STEP_ORDER[0]
        self._set_phase_step(first_phase, first_step)
        self._begin_step()

    # -------------------------------------------------------------------------
    # Step-specific handlers (hooks into rules layer)
    # -------------------------------------------------------------------------

    def _handle_untap_step(self):
        """
        Untap step:
        - No priority.
        - Active player's permanents untap via events/handlers.
        """
        self.gs.event_bus.publish(Event(
            type=EventType.UNTAP,
            payload={"active_player": self.state.active_player}
        ))
        # Untap implementation should be in rules handlers.

    def _handle_draw_step(self):
        """
        Draw step:
        - Active player draws a card (or replacement).
        - Triggers may be created (e.g. "Whenever you draw a card").
        """
        player = self.gs.players[self.state.active_player]

        # DRAW event opens replacement window and lets rules layer perform the draw.
        self.gs.event_bus.publish(Event(
            type=EventType.DRAW,
            payload={"player_id": player.id}
        ))

    def _handle_combat_damage_step(self):
        """
        Combat damage step:
        - Deal combat damage via combat engine / handlers.
        - Then players get priority.
        """
        self.gs.event_bus.publish(Event(
            type=EventType.COMBAT_DAMAGE,
            payload={
                "active_player": self.state.active_player,
                "turn_number": self.state.turn_number,
            }
        ))
        # Actual damage assignment/resolution should be done by a combat subsystem.

    def _handle_cleanup_step(self) -> bool:
        """
        Cleanup step:
        - Discard down to max hand size (rules layer).
        - Remove damage from creatures.
        - Clear "until end of turn" effects in rules layer.
        - Normally, no priority. But if SBAs or triggers cause changes,
          an additional cleanup is performed.

        Returns:
            True if an additional cleanup is required (rules layer decides),
            False otherwise.
        """
        self.gs.event_bus.publish(Event(
            type=EventType.CLEANUP,
            payload={
                "phase": self.state.phase,
                "step": self.state.step,
                "active_player": self.state.active_player,
                "turn_number": self.state.turn_number,
            }
        ))

        # Simple example: remove damage from creatures on battlefield.
        for obj in self.gs.objects.values():
            if getattr(obj.zone, "name", None) == "BATTLEFIELD":
                obj.damage = 0

        run_sbas(self.gs)

        # In a full engine, rules layer would signal if another cleanup is needed.
        # For now, assume no extra cleanup.
        return False

    # -------------------------------------------------------------------------
    # Convenience accessors for UI/engine loop
    # -------------------------------------------------------------------------

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
