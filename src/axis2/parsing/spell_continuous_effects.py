# axis2/parsing/spell_continuous_effects.py

import re
from axis2.schema import ContinuousEffect, PTExpression
from axis2.parsing.subject import parse_subject
from axis2.parsing.continuous_effects.pt_mod import parse_dynamic_counter_clause
from axis2.schema import ParseContext
from axis2.parsing.layers import assign_layer_to_effect

PT_RE = re.compile(r"get[s]?\s+([+\-]?\d+)\/([+\-]?\d+)", re.I)
DURATION_RE = re.compile(r"until end of turn|this turn|until your next turn", re.I)

def parse_spell_continuous_effect(text: str, ctx: ParseContext):
    t = text.lower()

    m = PT_RE.search(t)
    if not m:
        return None

    power = m.group(1)
    toughness = m.group(2)

    subject = parse_subject(t)
    if not subject:
        return None

    d = DURATION_RE.search(t)
    duration = d.group(0).lower() if d else None

    effect = ContinuousEffect(
        kind="pt_mod",
        applies_to=subject,
        pt_value=PTExpression(power=power, toughness=toughness),
        duration=duration,
        text=text,
        layer=7,  # Will be overridden by assign_layer_to_effect, but set default
        sublayer="7c",
        source_kind="spell",  # This is from a spell, not a static ability
    )

    # NEW: detect dynamic scaling
    dynamic = parse_dynamic_counter_clause(text, ctx)
    if dynamic:
        effect.dynamic = dynamic

    # Assign layer and sublayer
    assign_layer_to_effect(effect)

    return effect
