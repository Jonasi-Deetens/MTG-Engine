# axis3/engine/objects/flags.py

def can_attack(game_state, obj):
    """
    Engine-level logic for determining whether a permanent can attack.
    This will later include haste, restrictions, effects, etc.
    """
    if not obj.is_creature():
        return False

    if obj.tapped:
        return False

    # Haste check (via evaluated characteristics)
    ec = game_state.layers.evaluate(obj.id)
    has_haste = "haste" in ec.abilities

    if obj.summoning_sick and not has_haste:
        return False

    return True
