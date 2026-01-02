import re
from axis2.schema import ConditionalEffect

# All conditional patterns your engine supports
CONDITIONAL_PATTERNS = [
    ("exiled_this_way", re.compile(r"\bif [^.,;]* this way\b", re.I)),
    ("cast_it",         re.compile(r"\bif you cast it\b", re.I)),   # strict
    ("if_you_do",       re.compile(r"\bif you do\b", re.I)),
    ("kicked",          re.compile(r"\bif (it|this spell) was kicked\b", re.I)),
    ("modified_creature", re.compile(r"\bif you control a modified creature\b", re.I)),
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

    print(f"[parse_conditional] Starting parse: {repr(sentence)}")

    # --- PHASE A: Extract comma-delimited conditional clause
    m = COND_CLAUSE_RE.search(sentence)
    if m:
        cond_text = m.group(1).strip()          # e.g. "if you cast it"
        remainder = COND_CLAUSE_RE.sub(" ", sentence).strip()

        print(f"[parse_conditional] Found comma-delimited conditional")
        print(f"    cond_text: {repr(cond_text)}")
        print(f"    remainder: {repr(remainder)}")

        # Match the extracted condition against known patterns
        for name, regex in CONDITIONAL_PATTERNS:
            if regex.search(cond_text):
                print(f"    Matched pattern: {name} ({regex.pattern}) in {repr(cond_text)}")
                inner_effects = parse_effect_text(remainder, ctx)
                print(f"    Inner effects: {inner_effects}")
                return ConditionalEffect(condition=name, effects=inner_effects)

        print(f"    No conditional pattern matched for cond_text: {repr(cond_text)}")
        return None

    # --- PHASE B: Fallback — standalone conditional at sentence start
    for name, regex in CONDITIONAL_PATTERNS:
        m = regex.search(sentence)
        if m:
            print(f"[parse_conditional] Found standalone conditional - pattern {name} ({regex.pattern}) in {repr(sentence)}")
            inner = regex.sub("", sentence).strip().lstrip(",").strip()
            print(f"    Inner sentence after removing conditional: {repr(inner)}")
            inner_effects = parse_effect_text(inner, ctx)
            print(f"    Inner effects: {inner_effects}")
            return ConditionalEffect(condition=name, effects=inner_effects)

    print(f"[parse_conditional] No conditional found in: {repr(sentence)}")
    return None
