# src/axis3/engine/effects/resolve_effects.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.state.zones import ZoneType

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def count_objects(controller, count_source, gs):
    """
    Evaluate count_source strings like:
    - 'creature you control'
    - 'artifact you control'
    - 'each opponent'
    """
    src = count_source.lower()

    if src == "creature you control":
        return sum(
            1 for obj in gs.objects.values()
            if obj.controller == controller and obj.has_type("Creature")
        )

    if src == "artifact you control":
        return sum(
            1 for obj in gs.objects.values()
            if obj.controller == controller and obj.has_type("Artifact")
        )

    if src == "each opponent":
        return len([p for p in gs.players if p.id != controller])

    # Default fallback
    return 0


def create_token(gs, controller, power, toughness, colors, types, subtypes, source):
    """
    Create a RuntimeToken and put it on the battlefield.
    """
    token_id = gs.allocate_id()

    token = gs.create_token(
        id=token_id,
        controller=controller,
        power=power,
        toughness=toughness,
        colors=colors,
        types=types,
        subtypes=subtypes,
        source=source,
    )

    gs.move_card(token_id, ZoneType.BATTLEFIELD, controller)
    gs.event_bus.publish(Event(
        type=EventType.TOKEN_CREATED,
        payload={"token_id": token_id, "controller": controller}
    ))

    return token_id


# ------------------------------------------------------------
# Main Effect Resolver
# ------------------------------------------------------------

def resolve_effect(effect, gs, source_obj):
    selector = effect.selector
    params = effect.params

    # --------------------------------------------------------
    # Dynamic Token Creation
    # --------------------------------------------------------
    if selector == "create_dynamic_tokens":
        count = count_objects(source_obj.controller, params["count_source"], gs)
        for _ in range(count):
            create_token(
                gs=gs,
                controller=source_obj.controller,
                power=params["power"],
                toughness=params["toughness"],
                colors=params["colors"],
                types=params["types"],
                subtypes=params.get("subtypes", []),
                source=source_obj,
            )
        return

    # --------------------------------------------------------
    # Fixed Token Creation (if you use CreateTokenEffect)
    # --------------------------------------------------------
    if selector == "create_tokens":
        for _ in range(params["count"]):
            create_token(
                gs=gs,
                controller=source_obj.controller,
                power=params["power"],
                toughness=params["toughness"],
                colors=params["colors"],
                types=params["types"],
                subtypes=params.get("subtypes", []),
                source=source_obj,
            )
        return

    # --------------------------------------------------------
    # Deal Damage
    # --------------------------------------------------------
    if selector == "deal_damage":
        amount = params["amount"]
        target = params["target"]

        # Target is a RuntimeObject ID
        obj = gs.objects.get(target)
        if obj:
            obj.damage += amount
            gs.event_bus.publish(Event(
                type=EventType.DAMAGE,
                payload={"target": target, "amount": amount}
            ))
        return

    # --------------------------------------------------------
    # Draw Cards
    # --------------------------------------------------------
    if selector == "draw":
        amount = params["amount"]
        player_id = source_obj.controller

        for _ in range(amount):
            gs.event_bus.publish(Event(
                type=EventType.DRAW,
                payload={"player_id": player_id}
            ))
        return

    # --------------------------------------------------------
    # Add Mana
    # --------------------------------------------------------
    if selector == "add_mana":
        color = params["color"]
        player = gs.players[source_obj.controller]
        player.mana_pool[color] += 1

        gs.event_bus.publish(Event(
            type=EventType.ADD_MANA,
            payload={"player_id": player.id, "color": color}
        ))
        return

    # --------------------------------------------------------
    # Gain Life
    # --------------------------------------------------------
    if selector == "gain_life":
        amount = params["amount"]
        player = gs.players[source_obj.controller]
        player.life += amount

        gs.event_bus.publish(Event(
            type=EventType.GAIN_LIFE,
            payload={"player_id": player.id, "amount": amount}
        ))
        return

    # --------------------------------------------------------
    # Lose Life
    # --------------------------------------------------------
    if selector == "lose_life":
        amount = params["amount"]
        target = params["target"]
        player = gs.players[target]
        player.life -= amount

        gs.event_bus.publish(Event(
            type=EventType.LOSE_LIFE,
            payload={"player_id": target, "amount": amount}
        ))
        return

    # --------------------------------------------------------
    # Destroy
    # --------------------------------------------------------
    if selector == "destroy":
        target = params["target"]
        if target in gs.objects:
            gs.move_card(target, ZoneType.GRAVEYARD, gs.objects[target].controller)
            gs.event_bus.publish(Event(
                type=EventType.DESTROY,
                payload={"target": target}
            ))
        return

    # --------------------------------------------------------
    # Exile
    # --------------------------------------------------------
    if selector == "exile":
        target = params["target"]
        if target in gs.objects:
            gs.move_card(target, ZoneType.EXILE, gs.objects[target].controller)
            gs.event_bus.publish(Event(
                type=EventType.EXILE,
                payload={"target": target}
            ))
        return

    # --------------------------------------------------------
    # Bounce
    # --------------------------------------------------------
    if selector == "bounce":
        target = params["target"]
        if target in gs.objects:
            owner = gs.objects[target].owner
            gs.move_card(target, ZoneType.HAND, owner)
            gs.event_bus.publish(Event(
                type=EventType.BOUNCE,
                payload={"target": target}
            ))
        return

    # --------------------------------------------------------
    # Tap / Untap
    # --------------------------------------------------------
    if selector == "tap":
        target = params["target"]
        obj = gs.objects.get(target)
        if obj:
            obj.tapped = True
        return

    if selector == "untap":
        target = params["target"]
        obj = gs.objects.get(target)
        if obj:
            obj.tapped = False
        return

    # --------------------------------------------------------
    # Gain Control
    # --------------------------------------------------------
    if selector == "gain_control":
        target = params["target"]
        obj = gs.objects.get(target)
        if obj:
            obj.controller = source_obj.controller
        return

    # --------------------------------------------------------
    # Return from Graveyard
    # --------------------------------------------------------
    if selector == "return_from_gy":
        target = params["target"]
        dest = params["destination"]
        if target in gs.objects:
            gs.move_card(target, ZoneType.from_string(dest), source_obj.controller)
        return

    # --------------------------------------------------------
    # Unknown selector
    # --------------------------------------------------------
    gs.add_debug_log(f"[resolve_effect] Unknown selector: {selector}")
