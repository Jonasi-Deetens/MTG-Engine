# axis2/parsing/replacement_effects/patterns.py

"""Centralized regex patterns for reuse across replacement effect parsers"""
import re

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

RE_WOULD_BE_DESTROYED = re.compile(
    r"if (.*?) would be destroyed, (.*) instead",
    re.IGNORECASE | re.DOTALL
)

