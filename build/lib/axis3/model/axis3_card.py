# axis3/cards/card.py

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

from axis3.effects.base import Axis3Effect
from axis3.abilities.triggered import TriggeredAbility
from axis3.abilities.activated import ActivatedAbility
from axis3.effects.replacement import ReplacementEffect
from axis3.effects.static import StaticEffect


@dataclass
class Axis3Card:
    # Basic characteristics
    name: str
    mana_cost: Optional[str]
    mana_value: Optional[int]
    colors: List[str]
    color_identity: List[str]
    types: List[str]
    supertypes: List[str]
    subtypes: List[str]
    power: Optional[int]
    toughness: Optional[int]
    loyalty: Optional[int]
    defense: Optional[int]

    # Rules objects
    static_effects: List[StaticEffect] = field(default_factory=list)
    replacement_effects: List[ReplacementEffect] = field(default_factory=list)
    triggered_abilities: List[TriggeredAbility] = field(default_factory=list)
    activated_abilities: List[ActivatedAbility] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    # Spell effects (Axis3Effect objects)
    effects: List[Axis3Effect] = field(default_factory=list)

    # Special actions (Morph, Foretell, Prototype, Adventure)
    special_actions: List[Any] = field(default_factory=list)

    # Modal spells
    modes: List[Any] = field(default_factory=list)
    mode_choice: Optional[str] = None

    # Optional metadata for advanced mechanics
    metadata: Dict[str, Any] = field(default_factory=dict)
