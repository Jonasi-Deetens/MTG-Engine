# axis3/rules/layers/layer5.py

def apply_layer5(game_state, rt_obj, ec):
    """
    Apply abilities (keyword or activated) from static effects.
    """
    ec.abilities = set(rt_obj.characteristics.abilities)

    for eff in getattr(rt_obj.axis2, "static_effects", []):
        if eff.layer == 5:
            if hasattr(eff, "add_abilities"):
                ec.abilities.update(eff.add_abilities)
            if hasattr(eff, "remove_abilities"):
                ec.abilities.difference_update(eff.remove_abilities)

    return ec
