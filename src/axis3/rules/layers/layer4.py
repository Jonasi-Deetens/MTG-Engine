# axis3/rules/layers/layer4.py

def apply_layer4(game_state, rt_obj, ec):
    """
    Apply effects that modify:
    - Types
    - Colors
    - Subtypes
    - Supertypes
    """
    for eff in getattr(rt_obj.axis2, "static_effects", []):
        if eff.layer == 4:
            # Example: change color
            if hasattr(eff, "new_colors"):
                ec.colors = eff.new_colors

            # Example: add type
            if hasattr(eff, "add_types"):
                ec.types.update(eff.add_types)

            # Example: remove type
            if hasattr(eff, "remove_types"):
                ec.types.difference_update(eff.remove_types)

    return ec
