# axis2/parsing/effects/catch_all.py
"""Broad regex parsers for common oracle patterns (between specialized and fallback)."""

from __future__ import annotations

import re

from .base import EffectParser, ParseResult
from .patterns import NUMBER_WORDS
from axis2.schema import (
    ParseContext,
    DealDamageEffect,
    DrawCardsEffect,
    GainLifeEffect,
    LoseLifeEffect,
    MillEffect,
    FightEffect,
    CopyEffect,
    ProliferateEffect,
    VentureEffect,
    CreateTokenEffect,
    SymbolicValue,
    Subject,
)
from axis2.parsing.subject import subject_from_text


def _word_amount(word: str):
    w = word.lower().strip()
    if w.isdigit():
        return int(w)
    if w in NUMBER_WORDS:
        return NUMBER_WORDS[w]
    if w == "a" or w == "an":
        return 1
    return SymbolicValue(kind="variable", expression=w)


class AnyTargetDamageParser(EffectParser):
    priority = 55

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        t = text.lower()
        return "damage" in t and "deal" in t and "any target" in t

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = re.search(
            r"deals?\s+(\d+)\s+damage\s+to\s+any\s+target",
            text,
            re.I,
        )
        if not m:
            return ParseResult(matched=False)
        return ParseResult(
            matched=True,
            effect=DealDamageEffect(
                amount=int(m.group(1)),
                subject=Subject(scope="target", types=["any"]),
            ),
            consumed_text=text,
        )


class LoseLifeParser(EffectParser):
    priority = 48

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "lose" in text.lower() and "life" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = re.search(
            r"(?:each\s+)?opponents?\s+lose(?:s)?\s+(\d+)\s+life",
            text,
            re.I,
        )
        if m:
            return ParseResult(
                matched=True,
                effect=LoseLifeEffect(amount=int(m.group(1)), subject="each_opponent"),
                consumed_text=text,
            )
        m = re.search(r"target\s+player\s+loses\s+(\d+)\s+life", text, re.I)
        if m:
            return ParseResult(
                matched=True,
                effect=LoseLifeEffect(amount=int(m.group(1)), subject="target_player"),
                consumed_text=text,
            )
        m = re.search(r"you\s+lose\s+(\d+)\s+life", text, re.I)
        if m:
            return ParseResult(
                matched=True,
                effect=LoseLifeEffect(amount=int(m.group(1)), subject="you"),
                consumed_text=text,
            )
        return ParseResult(matched=False)


class MillParser(EffectParser):
    priority = 48

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "mill" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = re.search(
            r"mill(?:s)?\s+(?:a\s+)?(?:target\s+)?(?:player\s+)?(\w+)?\s*cards?",
            text,
            re.I,
        )
        if not m:
            m = re.search(r"(\w+)\s+cards?.*mill", text, re.I)
        amount = 1
        if m and m.group(1):
            amount = _word_amount(m.group(1))
        subj = Subject(scope="target", types=["player"])
        if "each opponent" in text.lower():
            subj = Subject(scope="each", controller="opponents", types=["player"])
        return ParseResult(
            matched=True,
            effect=MillEffect(amount=amount, subject=subj),
            consumed_text=text,
        )


class FightParser(EffectParser):
    priority = 48

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        t = text.lower()
        return "fight" in t or " battles " in t

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        optional = "may" in text.lower()
        if re.search(r"fight(?:s)?\s+target", text, re.I):
            return ParseResult(
                matched=True,
                effect=FightEffect(
                    subject=Subject(scope="target", types=["creature"]),
                    optional=optional,
                ),
                consumed_text=text,
            )
        return ParseResult(matched=False)


class CopySpellParser(EffectParser):
    priority = 45

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "copy" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if re.search(r"copy\s+(?:target\s+)?spell", text, re.I):
            return ParseResult(
                matched=True,
                effect=CopyEffect(target="target_spell", optional="may" in text.lower()),
                consumed_text=text,
            )
        if re.search(r"copy\s+that\s+spell", text, re.I):
            return ParseResult(
                matched=True,
                effect=CopyEffect(target="that_spell"),
                consumed_text=text,
            )
        return ParseResult(matched=False)


class ProliferateParser(EffectParser):
    priority = 40

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "proliferate" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        return ParseResult(
            matched=True,
            effect=ProliferateEffect(),
            consumed_text=text,
        )


class VentureParser(EffectParser):
    priority = 40

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        t = text.lower()
        return "venture" in t or "dungeon" in t

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        return ParseResult(
            matched=True,
            effect=VentureEffect(action=text.strip()[:200]),
            consumed_text=text,
        )


class DynamicTokenParser(EffectParser):
    """e.g. create a number of 2/2 black Zombie tokens equal to opponents."""

    priority = 65

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        t = text.lower()
        return "create" in t and "token" in t and ("equal to" in t or "number of" in t)

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = re.search(
            r"create\s+(?:a\s+)?number\s+of\s+(\d+)/(\d+)\s+(\w+)?\s*([\w\s]*?)\s*creature\s+tokens?\s+equal\s+to\s+(.+?)(?:\.|$)",
            text,
            re.I,
        )
        if not m:
            m = re.search(
                r"create\s+(?:a\s+)?number\s+of\s+(\d+)/(\d+)\s+([\w\s]+?)\s+tokens?\s+equal\s+to\s+(.+?)(?:\.|$)",
                text,
                re.I,
            )
        if not m:
            return ParseResult(matched=False)

        power, toughness = int(m.group(1)), int(m.group(2))
        color_word = (m.group(3) or "").strip().lower()
        subtype_text = (m.group(4) if m.lastindex >= 4 else "").strip()
        dynamic_expr = m.group(m.lastindex).strip().lower()

        colors = []
        from .patterns import COLOR_MAP
        if color_word in COLOR_MAP:
            colors.append(COLOR_MAP[color_word])

        subtypes = []
        for word in subtype_text.split():
            w = word.strip()
            if w and w not in ("creature", "token", "tokens") and w not in COLOR_MAP:
                subtypes.append(w.title())

        amount = SymbolicValue(kind="formula", expression=dynamic_expr.replace(" ", "_"))

        return ParseResult(
            matched=True,
            effect=CreateTokenEffect(
                amount=amount,
                token={
                    "power": power,
                    "toughness": toughness,
                    "colors": colors,
                    "types": ["Creature"],
                    "subtypes": subtypes,
                    "abilities": [],
                },
                controller="you",
            ),
            consumed_text=text,
        )

