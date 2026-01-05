# axis2/parsing/replacement_effects/damage.py

from typing import Optional
from .base import ReplacementEffectParser, ParseResult
from .patterns import RE_DAMAGE_PREVENTION
from axis2.schema import ReplacementEffect, Subject
from axis2.parsing.subject import subject_from_text
from axis2.schema import ParseContext
import re
import logging

logger = logging.getLogger(__name__)

# Pattern for damage redirection: "all damage that would be dealt [duration] to X is dealt to Y instead"
# This pattern handles:
# - "all damage that would be dealt this turn to you and permanents you control is dealt to enchanted creature instead"
# Note: The pattern uses non-greedy matching (.+?) to capture the subjects correctly
RE_DAMAGE_REDIRECTION = re.compile(
    r"(?:all\s+)?damage\s+that\s+would\s+be\s+dealt\s+(?:this\s+turn\s+)?to\s+(.+?)\s+is\s+dealt\s+to\s+(.+?)\s+instead",
    re.IGNORECASE | re.DOTALL
)

# Pattern for damage prevention: "prevent the next N damage"
RE_DAMAGE_PREVENT = re.compile(
    r"prevent\s+the\s+next\s+(\w+)\s+damage",
    re.IGNORECASE
)

class DamageParser(ReplacementEffectParser):
    """Parses damage prevention/redirection replacement effects"""
    priority = 35  # Medium priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        # Check for "damage" and "would be dealt" separately to match "damage that would be dealt"
        result = ("damage" in lower and "would be dealt" in lower) or ("prevent" in lower and "damage" in lower)
        logger.debug(f"[DamageParser] can_parse: '{text[:80]}...' -> {result}")
        return result

    def parse(self, text: str, ctx: Optional[ParseContext] = None) -> ParseResult:
        lower = text.lower()
        
        logger.debug(f"[DamageParser] Parsing: '{text[:100]}...'")
        
        # Try damage redirection pattern first (more specific)
        redir_match = RE_DAMAGE_REDIRECTION.search(text)
        print(f"[DamageParser PRINT] Regex match result: {redir_match is not None}")
        print(f"[DamageParser PRINT] Text being matched: '{text}'")
        print(f"[DamageParser PRINT] Pattern: {RE_DAMAGE_REDIRECTION.pattern}")
        logger.debug(f"[DamageParser] Regex match result: {redir_match is not None}")
        if redir_match:
            logger.debug(f"[DamageParser] Matched groups: 1='{redir_match.group(1)}', 2='{redir_match.group(2)}'")
            original_target_text = redir_match.group(1).strip()
            redirect_target_text = redir_match.group(2).strip()
            
            # Check for duration
            duration = None
            if "this turn" in lower:
                duration = "until_end_of_turn"
            
            # Parse subjects
            # Create a minimal context if none provided
            if ctx is None:
                ctx = ParseContext(
                    card_name="",
                    primary_type="enchantment",
                    face_name="",
                    face_types=[],
                    is_static_ability=False,
                    is_triggered_ability=True,
                    is_spell_text=False
                )
            
            # Parse original damage target (e.g., "you and permanents you control")
            original_subject = subject_from_text(original_target_text, ctx)
            
            # Parse redirect target (e.g., "enchanted creature")
            redirect_subject = subject_from_text(redirect_target_text, ctx)
            
            # Convert redirect subject to a string reference for the value field
            # "enchanted creature" -> "enchanted_creature"
            redirect_to = redirect_target_text.lower().replace(" ", "_")
            if "enchanted creature" in redirect_target_text.lower():
                redirect_to = "enchanted_creature"
            elif "you" in redirect_target_text.lower():
                redirect_to = "you"
            elif "this" in redirect_target_text.lower() and "creature" in redirect_target_text.lower():
                redirect_to = "self"
            
            effect = ReplacementEffect(
                kind="redirect_damage",
                event="would_be_dealt_damage",
                subject=original_subject,
                value={
                    "redirect_to": redirect_to,
                    "redirect_subject": redirect_subject
                },
                zones=["battlefield"],
                duration=duration,
                text=text
            )
            
            logger.debug(f"[DamageParser] Parsed damage redirection: {original_target_text} -> {redirect_target_text}")
            
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        
        # Try damage prevention pattern
        prevent_match = RE_DAMAGE_PREVENT.search(text)
        if prevent_match:
            amount = prevent_match.group(1).strip()
            if amount.isdigit():
                amount = int(amount)
            elif amount == "all":
                amount = "all"
            else:
                amount = "all"  # fallback

            effect = ReplacementEffect(
                kind="prevent_damage",
                event="would_be_dealt_damage",
                subject=Subject(scope="self"),
                value={"amount": amount},
                zones=["battlefield"],
                text=text
            )
            
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        
        # Fallback: check if it matches the basic pattern but we couldn't parse it
        if RE_DAMAGE_PREVENTION.search(text) and "instead" in lower:
            # Generic redirect without full parsing
            effect = ReplacementEffect(
                kind="redirect_damage",
                event="would_be_dealt_damage",
                subject=Subject(scope="self"),
                value={"action": "redirect"},
                zones=["battlefield"],
                text=text
            )
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )

        return ParseResult(matched=False)

