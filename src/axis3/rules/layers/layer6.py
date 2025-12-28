# axis3/rules/layers/layer6.py

def apply_layer6(game_state, rt_obj, ec):
    """
    Apply effects that set power/toughness (static, not counters).
    """
    for eff in getattr(rt_obj.axis2, "static_effects", []):
        if eff.layer == 6:
            if hasattr(eff, "set_power"):
                ec.power = eff.set_power
            if hasattr(eff, "set_toughness"):
                ec.toughness = eff.set_toughness

    return ec
