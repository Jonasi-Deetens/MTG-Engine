# axis2/parsing/effects/utils.py

import re
from typing import List

def split_effect_sentences(text: str) -> List[str]:
    """Extracted from original - no changes needed"""
    # DO NOT split on commas — they appear inside OR-lists.
    text = text.replace("\n", " ")

    # Normalize "then" into a sentence boundary
    text = re.sub(r"(?<!this way,)\s+then\b", ". then", text, flags=re.I)

    parts = re.split(r"[.;]", text)

    # Remove empty or whitespace-only parts BEFORE returning
    cleaned = []
    for p in parts:
        s = p.strip()
        if s:
            cleaned.append(s)

    return cleaned

