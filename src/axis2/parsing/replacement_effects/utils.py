# axis2/parsing/replacement_effects/utils.py

"""Shared utilities for replacement effect parsing"""
from axis2.schema import Subject

def parse_subject_from_text(raw: str) -> Subject:
    """Parse subject from text for replacement effects"""
    raw = raw.lower().strip()

    # Common subject references
    if raw in ("it", "this", "this creature", "this permanent", "this card"):
        return Subject(scope="self")

    # Fallback: assume self
    return Subject(scope="self")

def parse_instead_actions(text: str):
    """Parse 'instead' actions from text"""
    text = text.lower()
    actions = []

    if "reveal" in text:
        actions.append({"action": "reveal"})

    if "shuffle" in text and "library" in text:
        actions.append({"action": "shuffle_into_library"})

    if "exile" in text:
        actions.append({"action": "exile"})

    if "return" in text and "hand" in text:
        actions.append({"action": "return_to_hand"})

    return actions

def parse_delayed_subject(raw: str) -> Subject:
    """Parse subject for delayed replacement effects"""
    raw = raw.lower().strip()
    if "source of your choice" in raw:
        return Subject(scope="chosen_source")
    if "a source" in raw:
        return Subject(scope="source")
    return Subject(scope="self")

