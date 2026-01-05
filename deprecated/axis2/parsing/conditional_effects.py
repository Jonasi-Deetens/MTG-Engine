import re
from axis2.schema import ConditionalEffect

# All conditional patterns your engine supports
# Order matters: more specific patterns should come first
CONDITIONAL_PATTERNS = [
    ("discarded_this_way", re.compile(r"\bif [^.,;]* (?:is|are) discarded this way\b", re.I)),
    ("exiled_this_way", re.compile(r"\bif [^.,;]* (?:is|are) exiled this way\b", re.I)),
    ("cast_it",         re.compile(r"\bif you cast it\b", re.I)),   # strict
    ("if_you_do",       re.compile(r"\bif you do\b", re.I)),
    ("kicked",          re.compile(r"\bif (it|this spell) was kicked\b", re.I)),
    ("modified_creature", re.compile(r"\bif you control a modified creature\b", re.I)),
    ("havent_cast_spell", re.compile(r"\bif you haven'?t\s+cast\s+a\s+spell\s+from\s+your\s+hand\s+this\s+turn\b", re.I)),
]

COND_CLAUSE_RE = re.compile(
    r",\s*(if [^,.;]+?),\s*",
    re.I
)

def parse_conditional(sentence: str, ctx):
    """
    Detects conditional clauses and returns a ConditionalEffect if found.
    Handles both comma-delimited conditional clauses and standalone ones.
    """

    from axis2.parsing.effects import parse_effect_text

    lower = sentence.strip().lower()

    # Skip known non-conditional patterns
    # NEW: detect if the sentence contains a conditional clause BEFORE stripping 
    has_conditional = any(regex.search(sentence) for _, regex in CONDITIONAL_PATTERNS) 
    
    # OLD SKIP RULE — but now guarded 
    if not has_conditional: 
        if lower.startswith("you may"): 
            return None 
        if "you may search your library" in lower: 
            return None

    # --- PHASE A: Extract comma-delimited conditional clause
    m = COND_CLAUSE_RE.search(sentence)
    if m:
        cond_text = m.group(1).strip()          # e.g. "if you cast it"
        remainder = COND_CLAUSE_RE.sub(" ", sentence).strip()

        # Match the extracted condition against known patterns
        for name, regex in CONDITIONAL_PATTERNS:
            if regex.search(cond_text):
                inner_effects = parse_effect_text(remainder, ctx)
                return ConditionalEffect(condition=name, effects=inner_effects)

        return None

    # --- PHASE B: Handle "if you do" pattern specially
    # Pattern: "you may [action]. If you do, [effect]"
    if_you_do_match = re.search(r"\bif you do\b", sentence, re.I)
    if if_you_do_match:
        # Split at "if you do"
        split_pos = if_you_do_match.start()
        before_if = sentence[:split_pos].strip().rstrip(".").rstrip(",").strip()
        after_if = sentence[if_you_do_match.end():].strip().lstrip(",").strip()
        
        # Parse the "after" part as the conditional effect
        after_effects = parse_effect_text(after_if, ctx) if after_if else []
        
        # The "before" part might be:
        # 1. A cost (e.g., "you may pay {1}") - skip it, costs aren't effects
        # 2. An effect (e.g., "you may return another creature") - parse it
        all_effects = []
        
        # Check if "before" is just a cost (starts with "you may pay")
        if before_if.lower().startswith("you may pay"):
            # This is a cost, not an effect - skip it
            # The cost will be handled by Axis3 during resolution
            pass
        elif before_if.lower().startswith("you may"):
            # This might be an optional effect - try to parse it
            before_effects = parse_effect_text(before_if, ctx) if before_if else []
            all_effects.extend(before_effects)
        
        # Add the conditional effects (the "if you do" part)
        all_effects.extend(after_effects)
        
        return ConditionalEffect(condition="if_you_do", effects=all_effects)
    
    # --- PHASE C: Fallback — standalone conditional at sentence start
    for name, regex in CONDITIONAL_PATTERNS:
        if name == "if_you_do":  # Skip, already handled above
            continue
        m = regex.search(sentence)
        if m:
            inner = regex.sub("", sentence).strip().lstrip(",").strip()
            inner_effects = parse_effect_text(inner, ctx)
            return ConditionalEffect(condition=name, effects=inner_effects)

    return None
