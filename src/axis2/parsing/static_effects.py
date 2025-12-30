# axis2/parsing/static_effects.py

from axis2.schema import StaticEffect, DayboundEffect, NightboundEffect

def parse_static_effects(axis1_face):
    """
    Combine Axis1 static effects (if any) with Axis2-detected static effects
    like Daybound/Nightbound.
    """
    effects = []

    # ------------------------------------------------------------
    # 1. Axis1-provided static effects (rare but supported)
    # ------------------------------------------------------------
    raw_effects = getattr(axis1_face, "static_effects", [])
    for raw in raw_effects:
        effects.append(
            StaticEffect(
                kind=raw["kind"],
                subject=raw["subject"],
                value=raw["value"],
                layer=raw["layering"],
                zones=raw["zones"],
            )
        )

    # ------------------------------------------------------------
    # 2. Axis2-detected static effects from oracle text
    # ------------------------------------------------------------
    text = (axis1_face.oracle_text or "").lower()

    if "daybound" in text:
        effects.append(DayboundEffect())

    if "nightbound" in text:
        effects.append(NightboundEffect())

    return effects
