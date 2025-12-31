from axis2.schema import Subject
import re

def parse_subject(text: str) -> Subject | None:
    t = text.lower()

    # ----------------------------------------
    # 1. Scope detection
    # ----------------------------------------
    print(f"Parsing subject: {t}")
    # Plural subjects imply "each"
    if re.search(r"\bcreatures\b", t):
        scope = "each"
    elif "target" in t:
        scope = "target"
    elif "each" in t:
        scope = "each"
    elif "any number of" in t:
        scope = "any_number"
    elif "up to" in t:
        scope = "up_to_n"
    else:
        scope = None


    # ----------------------------------------
    # 2. Controller detection
    # ----------------------------------------
    controller = None
    if "you control" in t:
        controller = "you"
    elif "your opponents control" in t:
        controller = "opponents"
    elif "opponent controls" in t:
        controller = "opponent"
    elif "each opponent" in t:
        controller = "opponent"
    elif "opponent" in t:
        controller = "opponent"

    # ----------------------------------------
    # 3. Type detection
    # ----------------------------------------
    types = []
    for typ in ["creature", "player", "planeswalker", "artifact", "enchantment", "land", "permanent"]:
        if typ in t:
            types.append(typ)

    if not types:
        types = None

    # ----------------------------------------
    # 4. Filters (keywords, power, etc.)
    # ----------------------------------------
    filters = {}

    if "with flying" in t:
        filters["keyword"] = "flying"

    if "creature type of your choice" in t:
        filters["chosen_type"] = True



    # TODO: add more filters later

    if not filters:
        filters = None

    # ----------------------------------------
    # 5. Max targets (for "up to N targets")
    # ----------------------------------------
    max_targets = None
    m = re.search(r"up to (\d+)", t)
    if m:
        max_targets = int(m.group(1))

    # ----------------------------------------
    # 6. Return structured subject
    # ----------------------------------------
    if scope or controller or types or filters:
        return Subject(
            scope=scope,
            controller=controller,
            types=types,
            filters=filters,
            max_targets=max_targets
        )

    return None
