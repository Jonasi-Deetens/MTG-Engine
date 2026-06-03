# axis3/rules/handlers/begin_step_handler.py

from axis3.rules.events.types import EventType
from axis3.rules.events.event import Event

def handle_begin_step(gs: "GameState", event: Event):
    if "phase" not in event.payload or "step" not in event.payload:
        gs.add_debug_log("[RULES] BEGIN_STEP handler ignored malformed event")
        return

    phase = event.payload["phase"]
    step = event.payload["step"]
    prio = gs.turn_manager.priority.current
    # 1. Fire “at the beginning of step” triggers
    # (Your trigger system already handles this via event bus)

    gs.add_debug_log(f"[RULES] BEGIN_STEP: priority -> Player {prio}")
