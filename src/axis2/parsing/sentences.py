import re

def split_into_sentences(text: str) -> list[str]:
    """
    Splits Oracle text into meaningful MTG-style sentences.
    Handles periods, newlines, and em-dashes.
    """
    # Replace em-dashes with periods (they often separate clauses)
    text = text.replace("—", ". ")

    # Split on periods or newlines
    parts = re.split(r"\.\s+|\n+", text)

    # Clean up
    return [p.strip() for p in parts if p.strip()]
