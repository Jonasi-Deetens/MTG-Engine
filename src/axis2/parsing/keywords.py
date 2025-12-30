# axis2/parsing/keywords.py

def extract_keywords(oracle_text: str):
    """
    Extracts simple evergreen keywords that appear as standalone lines.
    """
    if not oracle_text:
        return []

    keywords = []
    lines = [l.strip() for l in oracle_text.split("\n")]

    evergreen = {
        "trample",
        "flying",
        "vigilance",
        "haste",
        "deathtouch",
        "lifelink",
        "reach",
        "menace",
        "first strike",
        "double strike",
        "hexproof",
        "ward",
    }

    for line in lines:
        lower = line.lower()
        if lower in evergreen:
            keywords.append(line)

    return keywords
