import re
from axis2.schema import ConditionalEffect

# All conditional patterns your engine supports
CONDITIONAL_PATTERNS = [
    ("exiled_this_way", re.compile(r"\bif .*?exile this way\b", re.I)),
    ("cast_it",         re.compile(r"\bif you cast it\b", re.I)),
    ("if_you_do",       re.compile(r"\bif you do\b", re.I)),
    ("kicked",          re.compile(r"\bif it was kicked\b", re.I)),
    ("modified_creature", re.compile(r"\bif you control a modified creature\b", re.I)),
]

def parse_conditional(sentence: str, ctx):
    """
    Detects conditional clauses and returns a ConditionalEffect if found.
    Otherwise returns None.
    """
    from axis2.parsing.effects import parse_effect_text
    for name, regex in CONDITIONAL_PATTERNS:
        m = regex.search(sentence)
        if m:
            # Remove the conditional phrase
            inner = regex.sub("", sentence).strip().lstrip(",").strip()
            inner_effects = parse_effect_text(inner, ctx)
            return ConditionalEffect(condition=name, effects=inner_effects)

    return None
