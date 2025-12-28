# axis3/rules/layers/layer7.py

def apply_layer7(game_state, rt_obj, ec):
    """
    Apply effects that modify power/toughness:
    - Counters
    - Buffs/Debuffs
    """
    # Apply +1/+1 counters
    if hasattr(rt_obj, "counters"):
        ec.power += rt_obj.counters.get("+1/+1", 0)
        ec.toughness += rt_obj.counters.get("+1/+1", 0)

    # Apply other modifiers from static effects
    for eff in getattr(rt_obj.axis2, "static_effects", []):
        if eff.layer == 7:
            if hasattr(eff, "pt_bonus"):
                ec.power += eff.pt_bonus.get("power", 0)
                ec.toughness += eff.pt_bonus.get("toughness", 0)

    return ec
