# axis3/rules/handlers/cleanup_handler.py

from axis3.rules.events.event import Event

def handle_cleanup(gs, event: Event):
    # Remove damage from creatures
    for obj in gs.objects.values():
        if obj.zone.name == "BATTLEFIELD":
            obj.damage = 0

    gs.add_debug_log("[RULES] Cleanup: removed damage")
