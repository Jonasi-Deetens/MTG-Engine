# axis2/parsing/effects/patterns.py
"""Centralized regex patterns for reuse across parsers"""
import re

# Number words
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10,
}

# Color mapping
COLOR_MAP = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}

# Common patterns
OPTIONAL_RE = re.compile(r"you may", re.IGNORECASE)
TARGET_RE = re.compile(r"\btarget\b", re.IGNORECASE)

