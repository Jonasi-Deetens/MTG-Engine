# axis3/rules/layers/layer1.py

def apply_layer1(game_state, rt_obj, ec):
    """
    Handle copy effects. These replace the base characteristics of an object.
    Must be applied first.
    """
    for eff in getattr(rt_obj.axis2, "static_effects", []):
        if eff.layer == 1 and hasattr(eff, "copy_source_id"):
            source_obj = game_state.objects.get(eff.copy_source_id)
            if source_obj:
                # Copy characteristics
                ec.types = source_obj.characteristics.types.copy()
                ec.subtypes = source_obj.characteristics.subtypes.copy()
                ec.supertypes = source_obj.characteristics.supertypes.copy()
                ec.colors = source_obj.characteristics.colors.copy()
                ec.abilities = source_obj.characteristics.abilities.copy()
                ec.power = source_obj.characteristics.power
                ec.toughness = source_obj.characteristics.toughness
    return ec
