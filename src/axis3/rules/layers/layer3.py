# axis3/rules/layers/layer3.py

def apply_layer3(game_state, rt_obj, ec):
    """
    Handle text-changing effects: ability or oracle text changes.
    """
    for eff in getattr(rt_obj.axis2, "static_effects", []):
        if eff.layer == 3:
            if hasattr(eff, "new_abilities"):
                ec.abilities = eff.new_abilities.copy()
            if hasattr(eff, "new_oracle_text"):
                ec.oracle_text = eff.new_oracle_text
    return ec
