"""
Layer assignment logic for MTG continuous effects.

MTG uses a 7-layer system for applying continuous effects:
- Layer 1: Copy effects
- Layer 2: Control-changing effects
- Layer 3: Text-changing effects
- Layer 4: Type-changing effects
- Layer 5: Color-changing effects
- Layer 6: Ability-adding/removing effects
- Layer 7: Power/toughness effects
  - 7a: Characteristic-defining abilities
  - 7b: Set P/T to specific value
  - 7c: Modify P/T
  - 7d: Counters
  - 7e: Switch P/T
"""

from typing import Optional
from axis2.schema import ContinuousEffect, StaticEffect


def assign_layer(effect: ContinuousEffect) -> tuple[int, Optional[str]]:
    """
    Assign layer and sublayer to continuous effect based on its kind.
    
    Returns:
        tuple[int, Optional[str]]: (layer, sublayer) where layer is 1-7
        and sublayer is None or "7a"-"7e" for layer 7.
    """
    kind = effect.kind
    
    # Layer 1: Copy effects
    if kind == "copy":
        return (1, None)
    
    # Layer 2: Control-changing effects
    if kind == "control_change":
        return (2, None)
    
    # Layer 3: Text-changing effects
    if kind == "text_change":
        return (3, None)
    
    # Layer 4: Type-changing effects
    if kind in ("type_set", "type_add", "type_remove", "subtype_set", "subtype_add", "subtype_remove"):
        return (4, None)
    
    # Layer 5: Color-changing effects
    if kind in ("color_set", "color_add", "color_remove"):
        return (5, None)
    
    # Layer 6: Ability-adding/removing effects
    if kind in ("grant_ability", "ability_remove_all", "grant_protection", "cant_be_blocked_by"):
        return (6, None)
    
    # Layer 7: Power/toughness effects
    if kind == "pt_set":
        return (7, "7b")  # Set P/T to specific value
    if kind == "pt_mod":
        return (7, "7c")  # Modify P/T
    if kind == "pt_characteristic_defining":
        return (7, "7a")  # Characteristic-defining abilities
    if kind == "pt_switch":
        return (7, "7e")  # Switch P/T
    # Counters are handled separately (7d), but we don't have a specific kind for that
    
    # Rule changes (targeting restrictions, etc.) - typically layer 6
    if kind == "rule_change":
        return (6, None)
    
    # Loss effects (ability/type removal) - layer 6 for abilities, layer 4 for types
    if kind == "ability_remove_all":
        return (6, None)
    if kind in ("type_remove_all", "subtype_remove_all"):
        return (4, None)
    
    # Default: assume layer 6 (abilities) if unknown
    # This is a safe fallback as most effects are ability-related
    return (6, None)


def assign_layer_to_effect(effect: ContinuousEffect) -> ContinuousEffect:
    """
    Assign layer and sublayer to a continuous effect, modifying it in place.
    
    Args:
        effect: The continuous effect to assign layers to
        
    Returns:
        The same effect object with layer and sublayer assigned
    """
    layer, sublayer = assign_layer(effect)
    effect.layer = layer
    effect.sublayer = sublayer
    return effect


def parse_static_layer(layer_str: str) -> tuple[int, Optional[str]]:
    """
    Convert string layer names to integer layer numbers for StaticEffect.
    
    Maps common string layer names to MTG layer numbers:
    - "abilities" -> 6
    - "rules" -> 6 (rule changes are typically layer 6)
    - "cost_modification" -> 6 (cost changes are typically layer 6)
    - "layer_7c" -> 7, "7c"
    - "layer_7b" -> 7, "7b"
    - etc.
    
    Args:
        layer_str: String layer name from old schema
        
    Returns:
        tuple[int, Optional[str]]: (layer, sublayer)
    """
    layer_str = layer_str.lower().strip()
    
    # Direct layer references
    if layer_str.startswith("layer_7"):
        sublayer = layer_str.replace("layer_", "")
        return (7, sublayer)
    if layer_str.startswith("7"):
        return (7, layer_str)
    
    # Named layers
    layer_map = {
        "abilities": 6,
        "rules": 6,
        "cost_modification": 6,
        "ability": 6,
        "type": 4,
        "color": 5,
        "control": 2,
        "text": 3,
        "copy": 1,
    }
    
    layer_num = layer_map.get(layer_str, 6)  # Default to layer 6 if unknown
    return (layer_num, None)

