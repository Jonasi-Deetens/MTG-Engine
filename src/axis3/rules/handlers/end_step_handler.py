# axis3/rules/handlers/end_step_handler.py

from axis3.rules.events.event import Event

def handle_end_step(gs, event: Event):
    phase = event.payload["phase"]
    step = event.payload["step"]

    # Nothing else needed yet — triggers fire automatically
    gs.add_debug_log(f"[RULES] END_STEP: {phase} / {step}")
