# src/axis3/rules/layers/layersystem.py

from typing import Dict, List, Set
from axis3.state.objects import RuntimeObject, RuntimeObjectId
from axis3.rules.layers.types import EvaluatedCharacteristics
from axis3.abilities.static import RuntimeContinuousEffect, RuntimeStaticAbility
from axis3.abilities.keyword import apply_keyword_abilities

class LayerSystem:
    """
    Central system for evaluating MTG layers 1–7 for all objects.
    Handles continuous effects, static abilities, and keyword abilities.
    """

    def __init__(self, game_state: "GameState"):
        self.game_state = game_state

    def evaluate(self, obj_id: RuntimeObjectId) -> EvaluatedCharacteristics:
        """
        Evaluate all characteristics for a permanent, applying static abilities in layer order.
        """
        rt_obj: RuntimeObject = self.game_state.objects[obj_id]

        # Base printed characteristics
        ec = EvaluatedCharacteristics(
            power=rt_obj.characteristics.power,
            toughness=rt_obj.characteristics.toughness,
            types=set(rt_obj.characteristics.types),
            subtypes=set(rt_obj.characteristics.subtypes),
            supertypes=set(rt_obj.characteristics.supertypes),
            colors=set(rt_obj.characteristics.colors),
            abilities=set(getattr(rt_obj.characteristics, "abilities", [])),
        )

        # Apply continuous effects from other objects
        ec = self._apply_continuous_effects(rt_obj, ec)

        # Apply layers 1–3 (type, supertype, subtype changes, if needed)
        ec = self._apply_layer1(rt_obj, ec)
        ec = self._apply_layer2(rt_obj, ec)
        ec = self._apply_layer3(rt_obj, ec)

        # Apply static abilities (layers 4–7)
        static_abilities: List[RuntimeStaticAbility] = getattr(rt_obj, "static_abilities", [])

        for layer_num in range(4, 8):
            layer_effects = []
            for sa in static_abilities:
                for eff in sa.effects:
                    if eff.layer == layer_num:
                        layer_effects.append((eff.sublayer or "", sa, eff))
            # sort sublayers (important for layer 7 P/T ordering)
            layer_effects.sort(key=lambda x: x[0])

            for _, sa, eff in layer_effects:
                sa.apply(self.game_state, obj_id, ec)

            # Layer 6: keyword abilities
            if layer_num == 6:
                ec = apply_keyword_abilities(self.game_state, rt_obj, ec)

        return ec

    def _apply_continuous_effects(
        self, rt_obj: RuntimeObject, ec: EvaluatedCharacteristics
    ) -> EvaluatedCharacteristics:
        """
        Apply all continuous effects from the game state that affect this object.
        """
        for ce in getattr(self.game_state, "continuous_effects", []):
            if not isinstance(ce, RuntimeContinuousEffect):
                continue
            if ce.applies_to(self.game_state, rt_obj.id):
                if ce.modify_power:
                    ec.power = ce.modify_power(self.game_state, rt_obj.id, ec.power)
                if ce.modify_toughness:
                    ec.toughness = ce.modify_toughness(self.game_state, rt_obj.id, ec.toughness)
                if ce.add_types:
                    ec.types.update(ce.add_types)
                if ce.add_subtypes:
                    ec.subtypes.update(ce.add_subtypes)
                if ce.add_supertypes:
                    ec.supertypes.update(ce.add_supertypes)
                if ce.add_colors:
                    ec.colors.update(ce.add_colors)
                if ce.add_abilities:
                    ec.abilities.update(ce.add_abilities)
                if ce.remove_abilities:
                    ec.abilities.difference_update(ce.remove_abilities)
        return ec

    # Dummy implementations for layers 1–3; expand as needed
    def _apply_layer1(self, rt_obj: RuntimeObject, ec: EvaluatedCharacteristics):
        # Supertype changes
        return ec

    def _apply_layer2(self, rt_obj: RuntimeObject, ec: EvaluatedCharacteristics):
        # Type changes
        return ec

    def _apply_layer3(self, rt_obj: RuntimeObject, ec: EvaluatedCharacteristics):
        # Subtype changes
        return ec
