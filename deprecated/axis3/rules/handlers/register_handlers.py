# axis3/rules/handlers/register_handlers.py

from axis3.rules.events.types import EventType

from axis3.rules.handlers.begin_step_handler import handle_begin_step
from axis3.rules.handlers.end_step_handler import handle_end_step
from axis3.rules.handlers.untap_handler import handle_untap_event
from axis3.rules.handlers.combat_damage_handler import handle_combat_damage
from axis3.rules.handlers.cleanup_handler import handle_cleanup
from axis3.rules.handlers.cast_handlers import handle_cast_spell

def register_all_handlers(gs: "GameState"):
    bus = gs.event_bus
    print("REGISTERING HANDLERS" + str(bus))
    print("BEGIN_STEP")
    bus.subscribe(EventType.BEGIN_STEP, handle_begin_step)
    bus.subscribe(EventType.END_STEP, handle_end_step)
    bus.subscribe(EventType.UNTAP, handle_untap_event)
    bus.subscribe(EventType.CAST_SPELL, handle_cast_spell)
    bus.subscribe(EventType.COMBAT_DAMAGE, handle_combat_damage)
    bus.subscribe(EventType.CLEANUP, handle_cleanup)
