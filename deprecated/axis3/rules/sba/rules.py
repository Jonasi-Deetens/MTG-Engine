# axis3/rules/sba/rules.py

from axis3.state.zones import ZoneType as Zone
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType


# ─────────────────────────────────────────────
# SBA: Creatures with lethal damage
# CR 704.5g
# ─────────────────────────────────────────────
def check_lethal_damage(game_state) -> bool:
    changed = False

    for obj in game_state.objects.values():
        if obj.zone != Zone.BATTLEFIELD:
            continue

        ec = game_state.layers.evaluate(obj.id)
        if "Creature" not in ec.types:
            continue
        if obj.damage >= ec.toughness:
            game_state.event_bus.publish(Event(
                type=EventType.ZONE_CHANGE,
                payload={
                    "obj_id": obj.id,
                    "from_zone": Zone.BATTLEFIELD,
                    "to_zone": Zone.GRAVEYARD,
                    "controller": obj.controller,
                    "cause": "lethal_damage",
                }
            ))
            changed = True

    return changed


# ─────────────────────────────────────────────
# SBA: Creatures with 0 or less toughness
# CR 704.5f
# ─────────────────────────────────────────────
def check_zero_toughness(game_state) -> bool:
    changed = False

    for obj in game_state.objects.values():
        if obj.zone != Zone.BATTLEFIELD:
            continue

        ec = game_state.layers.evaluate(obj.id)
        if "Creature" not in ec.types:
            continue
        if ec.toughness <= 0:
            game_state.event_bus.publish(Event(
                type=EventType.ZONE_CHANGE,
                payload={
                    "obj_id": obj.id,
                    "from_zone": Zone.BATTLEFIELD,
                    "to_zone": Zone.GRAVEYARD,
                    "controller": obj.controller,
                    "cause": "zero_toughness",
                }
            ))
            changed = True

    return changed


# ─────────────────────────────────────────────
# SBA: Tokens not on the battlefield cease to exist
# CR 704.5d
# ─────────────────────────────────────────────
def check_tokens(game_state) -> bool:
    changed = False

    for obj in list(game_state.objects.values()):
        if not obj.is_token:
            continue
        if obj.zone == Zone.BATTLEFIELD:
            continue

        # Tokens cease to exist — model as zone change to "void"
        game_state.event_bus.publish(Event(
            type=EventType.ZONE_CHANGE,
            payload={
                "obj_id": obj.id,
                "from_zone": obj.zone,
                "to_zone": None,          # interpreted as removal
                "controller": obj.controller,
                "cause": "token_cleanup",
            }
        ))
        changed = True

    return changed


# ─────────────────────────────────────────────
# SBA: Legend rule
# CR 704.5j
# ─────────────────────────────────────────────
def check_legend_rule(game_state) -> bool:
    changed = False

    for player in game_state.players:
        legends_by_name = {}

        for obj_id in player.battlefield:
            obj = game_state.objects[obj_id]
            ec = game_state.layers.evaluate(obj.id)
            if "Legendary" in ec.supertypes:
                name = obj.characteristics.name
                legends_by_name.setdefault(name, []).append(obj)

        for name, objs in legends_by_name.items():
            if len(objs) <= 1:
                continue

            # Player chooses one to keep
            # For now: keep the first, others die
            for obj in objs[1:]:
                game_state.event_bus.publish(Event(
                    type=EventType.ZONE_CHANGE,
                    payload={
                        "obj_id": obj.id,
                        "from_zone": Zone.BATTLEFIELD,
                        "to_zone": Zone.GRAVEYARD,
                        "controller": obj.controller,
                        "cause": "legend_rule",
                    }
                ))
                changed = True

    return changed
