# axis3/rules/atomic/dispatch.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType

from axis3.rules.atomic import draw
from axis3.rules.atomic import damage
from axis3.rules.atomic import life
from axis3.rules.atomic import zone_change


def apply_atomic_event(game_state, event: Event):
    """
    Apply the atomic game rule corresponding to the event type.
    This is the ONLY place that routes EventType → atomic rule.
    """

    if event.type == EventType.DRAW:
        draw.apply_draw(game_state, event)

    elif event.type == EventType.DAMAGE:
        damage.apply_damage(game_state, event)

    elif event.type == EventType.LIFE_CHANGE:
        life.apply_life_change(game_state, event)

    elif event.type == EventType.ZONE_CHANGE:
        zone_change.apply_zone_change(game_state, event)
    else:
        game_state.add_debug_log(f"Unhandled atomic event type: {event.type}")


    # Events that do not directly mutate game state
    # (e.g. CAST, TRIGGERED, ABILITY_ADDED) are intentionally ignored here
