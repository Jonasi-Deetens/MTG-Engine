# axis2/parsing/continuous_effects/patterns.py

"""Centralized regex patterns for reuse across continuous effect parsers"""
import re

# Number words
NUMBER_WORDS = {
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

# Color mapping
COLOR_WORD_TO_SYMBOL = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}

# Ability keywords
ABILITY_KEYWORDS = {
    "defender", "flying", "first strike", "double strike", "vigilance", "lifelink",
    "trample", "deathtouch", "haste", "reach", "menace", "hexproof",
    "indestructible", "ward"
}

# Clause boundaries for splitting
CLAUSE_BOUNDARIES = [
    " with base power and toughness ",
    " with base power & toughness ",
    ", has ",
    ", have ",
    " and has ",
    " and have ",
    ", gains ",
    ", gain ",
    " and gains ",
    " and gain ",
    " and it loses ",
    " and loses ",
]

# Regex patterns
PT_GETS_RE = re.compile(r"gets\s+([+\-]?\w+)\/([+\-]?\w+)", re.IGNORECASE)
HAS_ABILITY_RE = re.compile(r"has\s+(.+)", re.IGNORECASE)
GAINS_ABILITY_RE = re.compile(r"gains?\s+(.+)", re.IGNORECASE)
IS_COLOR_RE = re.compile(r"is\s+([a-z\s,]+)", re.IGNORECASE)
BASE_PT_RE = re.compile(r"base power and toughness\s+(\d+)\/(\d+)", re.IGNORECASE)
LOSES_ALL_RE = re.compile(r"loses\s+all\s+other?\s+(abilities|card types|creature types)", re.I)
FOR_EACH_COUNTER_RE = re.compile(
    r"for each (?P<counter>[\w\+\-\/]+) counter on (?P<subject>[^\.]+)",
    re.IGNORECASE
)
PROT_RE = re.compile(
    r"protection from ([^\n\.]+)",   # stop at newline or period
    re.I
)

