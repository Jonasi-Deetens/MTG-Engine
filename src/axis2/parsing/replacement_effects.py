# axis2/parsing/replacement_effects.py

import re
from typing import List, Optional
from axis2.schema import ReplacementEffect, Subject

# ------------------------------------------------------------
# Regex patterns for canonical replacement-effect templates
# ------------------------------------------------------------

RE_WOULD_DIE = re.compile(
    r"if (.*?) would die, (.*) instead",
    re.IGNORECASE | re.DOTALL
)

RE_WOULD_GO_TO_GRAVEYARD = re.compile(
    r"if (.*?) would be put into a graveyard from anywhere, (.*) instead",
    re.IGNORECASE | re.DOTALL
)

RE_ENTER_TAPPED = re.compile(
    r"enter(s)? the battlefield tapped",
    re.IGNORECASE
)

RE_DAMAGE_PREVENTION = re.compile(
    r"if (.*?) damage would be dealt",
    re.IGNORECASE
)

RE_DRAW_REPLACEMENT = re.compile(
    r"if (.*?) would draw",
    re.IGNORECASE
)

RE_DELAYED_REPLACEMENT = re.compile(
    r"the next time (.*?) would (.*?) this turn",
    re.IGNORECASE | re.DOTALL
)


# ------------------------------------------------------------
# Subject parsing helper
# ------------------------------------------------------------

def parse_subject_from_text(raw: str) -> Subject:
    raw = raw.lower().strip()

    # Common subject references
    if raw in ("it", "this", "this creature", "this permanent", "this card"):
        return Subject(scope="self")

    # Fallback: assume self
    return Subject(scope="self")


# ------------------------------------------------------------
# Action parsing helper
# ------------------------------------------------------------

def parse_instead_actions(text: str):
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
    raw = raw.lower().strip()
    if "source of your choice" in raw:
        return Subject(scope="chosen_source")
    if "a source" in raw:
        return Subject(scope="source")
    return Subject(scope="self")



# ------------------------------------------------------------
# Main replacement-effect parser
# ------------------------------------------------------------

def parse_replacement_effects(text: str) -> List[ReplacementEffect]:
    effects = []
    if not text:
        return effects

    lower = text.lower()
    m = RE_DELAYED_REPLACEMENT.search(text)
    if m:
        event_subject_raw = m.group(1)
        event_action_raw = m.group(2)

        # Example: "a source of your choice" → Subject(scope="chosen_source")
        subject = parse_delayed_subject(event_subject_raw)

        effects.append(
            ReplacementEffect(
                kind="delayed_prevent_damage",
                event="damage",
                subject=subject,
                value={"amount": "all"},
                zones=["anywhere"],
                next_event_only=True,
                duration="until_end_of_turn"
            )
        )

        return effects

    # --------------------------------------------------------
    # 1. Progenitus / Darksteel Colossus / Worldspine Wurm
    #    "If X would be put into a graveyard from anywhere, Y instead."
    # --------------------------------------------------------
    m = RE_WOULD_GO_TO_GRAVEYARD.search(text)
    if m:
        subject_raw = m.group(1)
        action_raw = m.group(2)

        subject = parse_subject_from_text(subject_raw)
        actions = parse_instead_actions(action_raw)

        effects.append(
            ReplacementEffect(
                kind="zone_change_replacement",
                event="move_to_graveyard",
                subject=subject,
                value={"instead": actions},
                zones=["anywhere"]
            )
        )
        return effects

    # --------------------------------------------------------
    # 2. Dies replacement
    #    "If X would die, Y instead."
    # --------------------------------------------------------
    m = RE_WOULD_DIE.search(text)
    if m:
        subject_raw = m.group(1)
        action_raw = m.group(2)

        subject = parse_subject_from_text(subject_raw)
        actions = parse_instead_actions(action_raw)

        effects.append(
            ReplacementEffect(
                kind="dies_replacement",
                event="would_die",
                subject=subject,
                value={"instead": actions},
                zones=["battlefield"]
            )
        )
        return effects

    # --------------------------------------------------------
    # 3. Enter tapped
    # --------------------------------------------------------
    if RE_ENTER_TAPPED.search(text):
        effects.append(
            ReplacementEffect(
                kind="enter_tapped",
                event="enter_battlefield",
                subject=Subject(scope="self"),
                value={"tapped": True},
                zones=["battlefield"]
            )
        )
        return effects

    # --------------------------------------------------------
    # 4. Damage prevention / redirection
    # --------------------------------------------------------
    if RE_DAMAGE_PREVENTION.search(text):
        if "prevent" in lower:
            # detect "prevent the next N damage"
            m = re.search(r"prevent the next (\w+)", lower)
            amount = m.group(1) if m else "all"

            effects.append(
                ReplacementEffect(
                    kind="prevent_damage",
                    event="damage",
                    subject=Subject(scope="self"),
                    value={"amount": amount},
                    zones=["battlefield"]
                )
            )
            return effects

        if "instead" in lower:
            effects.append(
                ReplacementEffect(
                    kind="redirect_damage",
                    event="damage",
                    subject=Subject(scope="self"),
                    value={"action": "redirect"},
                    zones=["battlefield"]
                )
            )
            return effects

    # --------------------------------------------------------
    # 5. Draw replacement
    # --------------------------------------------------------
    if RE_DRAW_REPLACEMENT.search(text):
        m = re.search(r"draw (\w+) instead", lower)
        amount = m.group(1) if m else None

        effects.append(
            ReplacementEffect(
                kind="draw_replacement",
                event="draw",
                subject=Subject(scope="self"),
                value={"amount": amount},
                zones=["anywhere"]
            )
        )
        return effects

    # --------------------------------------------------------
    # 6. No match
    # --------------------------------------------------------
    return effects
