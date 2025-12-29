# axis3/rules/stack/resolver.py

from axis3.engine.stack.item import StackItem
from axis3.rules.events.event import Event
from axis3.rules.replacement.apply import apply_replacements
from axis3.rules.atomic import zone_change, draw, damage, life
from axis3.rules.sba import run_sbas

def resolve_top_of_stack(game_state: "GameState"):
    """
    Resolve the top item on the stack (LIFO).
    Handles triggered abilities, activated abilities, permanents, spells, and lands.
    """
    if not game_state.stack or game_state.stack.is_empty():
        return

    item: StackItem = game_state.stack.pop()

    # -------------------------------
    # 1️⃣ Triggered Ability
    # -------------------------------
    if item.is_triggered_ability():
        resolve_runtime_triggered_ability(game_state, item.triggered_ability)
        run_sbas(game_state)
        return

    # -------------------------------
    # 2️⃣ Activated Ability
    # -------------------------------
    if item.is_activated_ability():
        raa = item.activated_ability
        # Apply costs, restrictions, and any replacement effects
        # For now, we just execute the effect
        raa.effect(game_state)
        run_sbas(game_state)
        return

    # -------------------------------
    # 3️⃣ Permanent or Land
    # -------------------------------
    obj_id = item.obj_id
    if obj_id is None or obj_id not in game_state.objects:
        return

    rt_obj = game_state.objects[obj_id]

    is_permanent = any(
        t in ("Creature", "Artifact", "Enchantment", "Planeswalker", "Land", "Battle")
        for t in rt_obj.characteristics.types
    )

    # Determine target zone
    if is_permanent:
        to_zone = "BATTLEFIELD"
    else:
        # Non-permanent spell goes to graveyard after resolution
        to_zone = "GRAVEYARD"

    # -------------------------------
    # 4️⃣ Handle tokens separately
    # -------------------------------
    if rt_obj.is_token and not is_permanent:
        # Tokens disappear after resolution
        del game_state.objects[rt_obj.id]
        run_sbas(game_state)
        return

    # -------------------------------
    # 5️⃣ Apply zone change with replacements
    # -------------------------------
    event = Event(
        type="zone_change",
        payload={
            "obj_id": rt_obj.id,
            "from_zone": rt_obj.zone,
            "to_zone": to_zone,
            "controller": item.controller,
            "cause": "resolution",
        }
    )

    event = apply_replacements(game_state, event)
    zone_change.apply_zone_change(game_state, event)

    # -------------------------------
    # 6️⃣ Handle lands entering tapped/untapped
    # -------------------------------
    if "Land" in rt_obj.characteristics.types:
        # Check for replacement effects (e.g., ETB tapped)
        # Already applied via replacements above
        pass

    # -------------------------------
    # 7️⃣ Update game state after resolution
    # -------------------------------
    run_sbas(game_state)
    

def resolve_stack(game_state: "GameState"):
    """
    Resolve all items on the stack (LIFO) until empty.
    """
    while game_state.stack and not game_state.stack.is_empty():
        resolve_top_of_stack(game_state)
