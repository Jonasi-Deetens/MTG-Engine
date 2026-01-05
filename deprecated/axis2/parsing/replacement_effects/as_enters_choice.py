# axis2/parsing/replacement_effects/as_enters_choice.py

import re
import logging
from typing import Optional
from .base import ReplacementEffectParser, ParseResult
from axis2.schema import ReplacementEffect, Subject

logger = logging.getLogger(__name__)

RE_AS_ENTERS_CHOOSE_COLOR = re.compile(
    r"as\s+(?:this|it|that)\s+.*?enters(?:\s+the\s+battlefield)?[, ]\s*choose\s+a\s+color",
    re.IGNORECASE
)

RE_AS_ENTERS_CHOOSE_CREATURE_TYPE = re.compile(
    r"as\s+(?:this|it|that)\s+.*?enters(?:\s+the\s+battlefield)?[, ]\s*choose\s+a\s+creature\s+type",
    re.IGNORECASE
)

RE_AS_ENTERS_CHOOSE_PLAYER = re.compile(
    r"as\s+(?:this|it|that)\s+.*?enters(?:\s+the\s+battlefield)?[, ]\s*choose\s+(?:an?\s+)?(?:opponent|player)",
    re.IGNORECASE
)

RE_AS_ENTERS_CHOOSE_GENERIC = re.compile(
    r"as\s+(?:this|it|that)\s+.*?enters(?:\s+the\s+battlefield)?[, ]\s*choose\s+(.+?)(?:\.|$)",
    re.IGNORECASE
)


class AsEntersChoiceParser(ReplacementEffectParser):
    """Parses 'as enters' replacement effects that create choices"""
    priority = 48  # Higher than enter_tapped but lower than destruction
    
    def can_parse(self, text: str) -> bool:
        lower = text.lower()
        return ("as" in lower and "enters" in lower and "choose" in lower) or \
               ("as" in lower and "enter" in lower and "choose" in lower)
    
    def parse(self, text: str) -> ParseResult:
        logger.debug(f"[AsEntersChoiceParser] Parsing: {text[:100]}")
        
        # Check for specific choice types
        if RE_AS_ENTERS_CHOOSE_COLOR.search(text):
            effect = ReplacementEffect(
                kind="as_enters_choice",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={
                    "choice_type": "color",
                    "choices": ["white", "blue", "black", "red", "green"]
                },
                zones=["battlefield"],
                text=text
            )
            logger.debug(f"[AsEntersChoiceParser] Created color choice replacement effect")
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        
        if RE_AS_ENTERS_CHOOSE_CREATURE_TYPE.search(text):
            effect = ReplacementEffect(
                kind="as_enters_choice",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={
                    "choice_type": "creature_type",
                    "choices": "all_creature_types"  # Axis3 resolves this
                },
                zones=["battlefield"],
                text=text
            )
            logger.debug(f"[AsEntersChoiceParser] Created creature type choice replacement effect")
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        
        if RE_AS_ENTERS_CHOOSE_PLAYER.search(text):
            effect = ReplacementEffect(
                kind="as_enters_choice",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={
                    "choice_type": "player",
                    "choices": "players"  # Axis3 resolves this
                },
                zones=["battlefield"],
                text=text
            )
            logger.debug(f"[AsEntersChoiceParser] Created player choice replacement effect")
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        
        # Generic "as enters, choose..." pattern
        m = RE_AS_ENTERS_CHOOSE_GENERIC.search(text)
        if m:
            choice_text = m.group(1).strip()
            logger.debug(f"[AsEntersChoiceParser] Found generic choice: {choice_text}")
            
            effect = ReplacementEffect(
                kind="as_enters_choice",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={
                    "choice_type": "generic",
                    "choice_description": choice_text
                },
                zones=["battlefield"],
                text=text
            )
            logger.debug(f"[AsEntersChoiceParser] Created generic choice replacement effect")
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        
        logger.debug(f"[AsEntersChoiceParser] No match found")
        return ParseResult(matched=False)

