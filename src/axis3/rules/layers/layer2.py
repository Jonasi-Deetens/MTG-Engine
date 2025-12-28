# axis3/rules/layers/layer2.py

def apply_layer2(game_state, rt_obj, ec):
    """
    Handle control-changing effects (gain control of permanent).
    Must be applied before layers that care about who controls the object.
    """
    for eff in getattr(rt_obj.axis2, "static_effects", []):
        if eff.layer == 2 and hasattr(eff, "new_controller"):
            rt_obj.controller = eff.new_controller
    return ec
