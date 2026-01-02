# axis2/parsing/static_effects/patterns.py

"""Centralized regex patterns for reuse across static effect parsers"""
import re

# Number words
NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

# Regex patterns
BLOCKING_RESTRICTION_RE = re.compile(
    r"each creature you control can\s*'?t?\s*be blocked by more than (\w+)",
    re.IGNORECASE
)

CREW_POWER_RE = re.compile(
    r"crews vehicles as though its power were (\w+) greater",
    re.IGNORECASE
)

HASTE_GRANT_RE = re.compile(
    r"all creatures have haste",
    re.IGNORECASE
)

TOP_REVEAL_RE = re.compile(
    r"play with the top card of their libraries revealed",
    re.IGNORECASE
)

ZONE_ADD_RE = re.compile(
    r"noninstant, nonsorcery cards on top of a library are on the battlefield",
    re.IGNORECASE
)

COST_MOD_RE = re.compile(
    r"(?P<types>[a-zA-Z ,]+?) spells? (?P<controller>you|your opponents?|opponents?) cast cost \{(?P<amount>\d+)\} (?P<direction>less|more) to cast",
    re.IGNORECASE
)

