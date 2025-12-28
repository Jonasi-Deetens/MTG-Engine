# axis3/rules/layers/system.py

from typing import Dict
from axis3.state.objects import RuntimeObject
from axis3.abilities.static import RuntimeStaticAbility
from axis3.state.game_state import GameState

@dataclass
class EvaluatedCharacteristics:
    """
    Holds the final characteristics of a permanent after applying layers.
    """
    power: int
    toughness: int
    types: set
    subtypes: set
    supertypes: set
    colors: set
    abilities: set


def evaluate_characteristics(game_state: GameState, obj_id: int) -> EvaluatedCharacteristics:
    """
    Evaluate all characteristics for a permanent, applying static abilities in layer order.
    """
    rt_obj: RuntimeObject = game_state.objects[obj_id]
    ec = EvaluatedCharacteristics(
        power=rt_obj.characteristics.power,
        toughness=rt_obj.characteristics.toughness,
        types=set(rt_obj.characteristics.types),
        subtypes=set(rt_obj.characteristics.subtypes),
        supertypes=set(rt_obj.characteristics.supertypes),
        colors=set(rt_obj.characteristics.colors),
        abilities=set(rt_obj.characteristics.abilities)
    )

    # Apply Layer 1–3 hardcoded effects (if any)
    ec = apply_layer1(game_state, rt_obj, ec)
    ec = apply_layer2(game_state, rt_obj, ec)
    ec = apply_layer3(game_state, rt_obj, ec)

    # Apply static abilities (layers 4–7)
    static_abilities: List[RuntimeStaticAbility] = getattr(rt_obj, "static_abilities", [])
    for layer_num in range(4, 8):
        # sort by sublayer if needed (e.g., 7a, 7b)
        layer_effects = []
        for sa in static_abilities:
            for eff in sa.effects:
                if eff.layer == layer_num:
                    layer_effects.append((eff.sublayer or "", sa, eff))
        # optional: sort by sublayer for Layer 7 P/T ordering
        layer_effects.sort(key=lambda x: x[0])

        for _, sa, eff in layer_effects:
            sa.apply(game_state, obj_id, ec)

    return ec
