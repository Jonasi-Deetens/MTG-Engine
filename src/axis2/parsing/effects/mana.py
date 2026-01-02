# axis2/parsing/effects/mana.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import AddManaEffect, ParseContext
from .patterns import NUMBER_WORDS

ADD_MANA_OR_RE = re.compile(
    r"add\s+(\{[^}]+\})\s+or\s+(\{[^}]+\})",
    re.IGNORECASE
)
# 1. Fixed mana symbols: "Add {R}{G}", "Add {C}", "Add {2}"
ADD_MANA_FIXED_RE = re.compile(r"add ((\{[^}]+\})+)", re.IGNORECASE)

# 2. Any color: "Add one mana of any color"
ADD_MANA_ANY_COLOR_RE = re.compile(r"add (one|1) mana of any color", re.IGNORECASE)

# 3. Any type: "Add one mana of any type"
ADD_MANA_ANY_TYPE_RE = re.compile(r"add (one|1) mana of any type", re.IGNORECASE)

# 4. Combination: "Add two mana in any combination of colors"
ADD_MANA_COMBO_RE = re.compile(
    r"add (\w+) mana in any combination of colors", re.IGNORECASE
)

class ManaParser(EffectParser):
    """Parses mana effects: 'Add {R}', 'Add one mana of any color', etc."""
    priority = 30  # Generic effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "add" in text.lower() and "mana" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        t = text.lower()
        
        # NEW: Choice between fixed symbols: "Add {U} or {R}"
        m = ADD_MANA_OR_RE.search(text)
        if m:
            sym1, sym2 = m.group(1), m.group(2)
            return ParseResult(
                matched=True,
                effect=AddManaEffect(mana=[sym1, sym2], choice="one_color"),
                consumed_text=text
            )

        # 1. Fixed mana symbols
        m = ADD_MANA_FIXED_RE.search(text)
        if m:
            symbols = re.findall(r"\{[^}]+\}", m.group(1))
            return ParseResult(
                matched=True,
                effect=AddManaEffect(mana=symbols, choice=None),
                consumed_text=text
            )

        # 2. Any color
        m = ADD_MANA_ANY_COLOR_RE.search(t)
        if m:
            return ParseResult(
                matched=True,
                effect=AddManaEffect(mana=[], choice="any_color"),
                consumed_text=text
            )

        # 3. Any type
        m = ADD_MANA_ANY_TYPE_RE.search(t)
        if m:
            return ParseResult(
                matched=True,
                effect=AddManaEffect(mana=[], choice="any_type"),
                consumed_text=text
            )

        # 4. Combination of colors
        m = ADD_MANA_COMBO_RE.search(t)
        if m:
            raw = m.group(1)
            amount = NUMBER_WORDS.get(raw, None)
            if amount:
                return ParseResult(
                    matched=True,
                    effect=AddManaEffect(mana=[], choice=f"combo_colors_{amount}"),
                    consumed_text=text
                )

        return ParseResult(matched=False)

