# axis2/parsing/triggers/patterns.py

"""Centralized regex patterns for reuse across trigger parsers"""
import re

ENTERS_RE = re.compile(
    r"\bwhenever\b.*\benters\b",
    re.IGNORECASE
)

ETB_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+enters(?:\s+the\s+battlefield)?",
    re.IGNORECASE
)

LTB_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+leaves\s+the\s+battlefield",
    re.IGNORECASE
)

DIES_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+dies",
    re.IGNORECASE
)

ATTACKS_RE = re.compile(
    r"\bwhenever\b.*\battacks\b",
    re.IGNORECASE
)

ZONE_CHANGE_TRIGGER_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+is\s+put\s+into\s+(?:an?\s+)?(\w+)\s+from\s+(?:the\s+)?(\w+)",
    re.IGNORECASE
)

DEALS_DAMAGE_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+deals\s+(combat\s+|noncombat\s+)?damage\s+to\s+(.*)",
    re.IGNORECASE
)

CAST_SPELL_RE = re.compile(
    r"(?:when|whenever)\s+(you|an opponent|a player|any player)\s+cast[s]?\s+(.*)",
    re.IGNORECASE
)

