# axis2/parsing/effects/tokens.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import CreateTokenEffect, SymbolicValue, ParseContext
from .patterns import COLOR_MAP, NUMBER_WORDS

GENERAL_TOKEN_RE = re.compile(
    r"create (\w+) (\d+)/(\d+) ([a-z ]+? creature) tokens?(?: with ([a-z ,]+))?",
    re.IGNORECASE
)

SIMPLE_TOKEN_RE = re.compile(
    r"create (\w+) ([a-z ]+? creature) tokens?",
    re.IGNORECASE
)

SIMPLE_ARTIFACT_TOKEN_RE = re.compile(
    r"create (?:a|an|one)?\s*(treasure|food|clue|blood|gold)\s+token",
    re.IGNORECASE
)

def parse_amount(word: str):
    word = word.lower()
    if word.isdigit():
        return int(word)
    if word in NUMBER_WORDS:
        return NUMBER_WORDS[word]
    if word == "x":
        return SymbolicValue(kind="variable", expression="X")
    return 1  # fallback

class TokenParser(EffectParser):
    """Parses token creation effects"""
    priority = 60  # Common effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "create" in text.lower() and "token" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        t = text.lower()

        # ------------------------------------------------------------
        # Pattern 1: Full creature token with stats
        # ------------------------------------------------------------
        m = GENERAL_TOKEN_RE.search(t)
        if m:
            amount_word = m.group(1)
            power = int(m.group(2))
            toughness = int(m.group(3))
            raw_types = m.group(4).strip()
            raw_abilities = m.group(5).strip() if m.group(5) else ""

            amount = parse_amount(amount_word)

            # Parse colors and types
            colors = []
            types = []
            subtypes = []
            color_words = ["white", "blue", "black", "red", "green"]
            special_words = ["colorless"]  # don't convert this to a subtype

            parts = raw_types.split()
            for p in parts:
                if p in color_words:
                    colors.append(COLOR_MAP[p])
                elif p == "artifact":
                    types.append("Artifact")
                elif p == "creature":
                    types.append("Creature")
                elif p in special_words:
                    # ignore "colorless" for now; colors=[] already encodes it
                    continue
                else:
                    subtypes.append(p.capitalize())

            # Parse abilities (optional)
            abilities = []
            if raw_abilities:
                abilities = [a.strip().capitalize() for a in raw_abilities.split(",")]

            return ParseResult(
                matched=True,
                effect=CreateTokenEffect(
                    amount=amount,
                    token={
                        "name": None,
                        "power": power,
                        "toughness": toughness,
                        "colors": colors,
                        "types": types,
                        "subtypes": subtypes,
                        "abilities": abilities,
                    },
                    controller="you",
                ),
                consumed_text=text
            )

        # ------------------------------------------------------------
        # Pattern 2: Simple artifact tokens (Treasure, Food, Clue, Blood, Gold)
        # ------------------------------------------------------------
        m = SIMPLE_ARTIFACT_TOKEN_RE.search(t)
        if m:
            token_name = m.group(1).strip().capitalize()

            return ParseResult(
                matched=True,
                effect=CreateTokenEffect(
                    amount=1,
                    token={
                        "name": token_name,
                        "power": None,
                        "toughness": None,
                        "colors": [],
                        "types": ["Artifact"],
                        "subtypes": [token_name],
                        "abilities": [],
                    },
                    controller="you",
                ),
                consumed_text=text
            )

        # ------------------------------------------------------------
        # Pattern 3: Simple creature tokens
        # ------------------------------------------------------------
        m = SIMPLE_TOKEN_RE.search(t)
        if m:
            amount_word = m.group(1)
            token_name = m.group(2).strip().capitalize()

            amount = parse_amount(amount_word)

            return ParseResult(
                matched=True,
                effect=CreateTokenEffect(
                    amount=amount,
                    token={
                        "name": token_name,
                        "power": None,
                        "toughness": None,
                        "colors": [],
                        "types": ["Artifact"],
                        "subtypes": [token_name],
                        "abilities": [],
                    },
                    controller="you",
                ),
                consumed_text=text
            )

        return ParseResult(matched=False)

