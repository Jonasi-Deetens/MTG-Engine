from axis3.state.zones import ZoneType
from axis3.state.game_state import GameState

def _perform_zone_change(game_state: GameState, event: dict) -> None:
    obj_id = event["obj_id"]
    rt_obj = game_state.objects[obj_id]

    old_zone = event["from_zone"]
    new_zone = event["to_zone"]

    # 1. Remove from old zone
    if old_zone == ZoneType.STACK:
        # The object was already popped from the stack by resolve_top_of_stack.
        # No per-player zone to clean up here.
        pass
    else:
        ps = game_state.players[rt_obj.owner]
        getattr(ps, old_zone.name.lower()).remove(obj_id)

    # 2. Add to new zone
    if new_zone == ZoneType.STACK:
        # If you ever push directly via zone change, you'd handle it here.
        # For now, we assume stack pushes are handled by cast/ability functions.
        pass
    else:
        ps = game_state.players[rt_obj.owner]
        getattr(ps, new_zone.name.lower()).append(obj_id)

    # 3. Update runtime object zone
    rt_obj.zone = new_zone
