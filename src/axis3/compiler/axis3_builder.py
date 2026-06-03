# axis3/compiler/axis3_builder.py
"""
DEPRECATED — do not use for new code.

This module attempted to build Axis3Card by re-parsing oracle text with a
*second* regex stack (axis3/rules/builder + effect_compiler). That duplicates
Axis2, diverges from coverage metrics, and was incomplete/broken.

Use instead:
  axis2.build_pipeline.Axis2BuildPipeline
  axis3.integration.runtime_loader.create_runtime_object
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from axis1.schema import Axis1Card
from axis2.build_pipeline import Axis2BuildPipeline
from axis3.model.axis3_card import Axis3Card
from axis3.rules.costs.mana import parse_mana_cost

if TYPE_CHECKING:
    from axis3.state.game_state import GameState


class Axis3CardBuilder:
    """
    Minimal compatibility shim: builds a lightweight Axis3Card shell from Axis1.

    Runtime abilities are NOT populated here — use create_runtime_object() with
    the returned Axis2 data via compile_axis2() in integration.runtime_loader.
    """

    @staticmethod
    def build(axis1_card: Axis1Card, game_state: "GameState | None" = None) -> Axis3Card:
        warnings.warn(
            "Axis3CardBuilder is deprecated; use axis3.integration.runtime_loader",
            DeprecationWarning,
            stacklevel=2,
        )
        face = axis1_card.faces[0]
        axis2 = Axis2BuildPipeline().build(axis1_card)

        mana_cost = parse_mana_cost(face.mana_cost)
        return Axis3Card(
            name=face.name,
            mana_cost=mana_cost,
            mana_value=getattr(face, "mana_value", None),
            colors=list(face.colors or []),
            color_identity=list(axis1_card.characteristics.color_identity or []),
            types=list(face.card_types or []),
            supertypes=list(face.supertypes or []),
            subtypes=list(face.subtypes or []),
            power=int(face.power) if face.power is not None and str(face.power).isdigit() else None,
            toughness=int(face.toughness) if face.toughness is not None and str(face.toughness).isdigit() else None,
            loyalty=face.loyalty if isinstance(face.loyalty, int) else None,
            defense=face.defense if isinstance(face.defense, int) else None,
            keywords=list(axis2.keywords or []),
            metadata={"axis2_built": True, "spell_effect_count": len(axis2.faces[0].spell_effects)},
        )
