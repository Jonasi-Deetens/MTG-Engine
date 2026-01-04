# axis2/parsing/replacement_effects/destruction.py

from typing import Optional, List
import logging
from .base import ReplacementEffectParser, ParseResult
from .patterns import RE_WOULD_BE_DESTROYED
from axis2.schema import ReplacementEffect, Subject

logger = logging.getLogger(__name__)


def parse_destruction_instead_actions(text: str) -> List[dict]:
    """Parse 'instead' actions for destruction replacement effects"""
    text = text.lower().strip()
    actions = []
    
    if "remove all damage" in text or "remove damage" in text:
        if "from it" in text or "from enchanted creature" in text:
            actions.append({
                "action": "remove_damage",
                "subject": "enchanted_creature"
            })
        else:
            actions.append({
                "action": "remove_damage",
                "subject": "self"
            })
    
    if "destroy this aura" in text or "destroy this enchantment" in text:
        actions.append({
            "action": "destroy",
            "subject": "self"
        })
    
    if "exile" in text:
        actions.append({
            "action": "exile",
            "subject": "self"
        })
    
    if "return" in text and "hand" in text:
        actions.append({
            "action": "return_to_hand",
            "subject": "self"
        })
    
    return actions


def parse_destruction_subject(raw: str) -> Subject:
    """Parse subject for destruction replacement effects"""
    raw = raw.lower().strip()
    
    if "enchanted creature" in raw:
        return Subject(scope="enchanted_creature")
    
    if raw in ("it", "this", "this creature", "this permanent", "this card"):
        return Subject(scope="self")
    
    return Subject(scope="self")


class DestructionParser(ReplacementEffectParser):
    """Parses destruction replacement effects: 'if X would be destroyed, Y instead'"""
    priority = 46
    
    def can_parse(self, text: str) -> bool:
        result = "would be destroyed" in text.lower() and "instead" in text.lower()
        logger.debug(f"[DestructionParser] can_parse('{text[:80]}'): {result}")
        return result
    
    def parse(self, text: str) -> ParseResult:
        logger.debug(f"[DestructionParser] parse called with: {text[:100]}")
        m = RE_WOULD_BE_DESTROYED.search(text)
        if not m:
            logger.debug(f"[DestructionParser] Regex did not match: {text[:100]}")
            return ParseResult(matched=False)
        
        logger.debug(f"[DestructionParser] Regex matched! Group 1: '{m.group(1)}', Group 2: '{m.group(2)}'")
        
        try:
            subject_raw = m.group(1).strip()
            action_raw = m.group(2).strip()
            
            subject = parse_destruction_subject(subject_raw)
            actions = parse_destruction_instead_actions(action_raw)
            
            logger.debug(f"[DestructionParser] Parsed subject: {subject.scope}, actions: {actions}")
            
            effect = ReplacementEffect(
                kind="prevent_destruction",
                event="would_be_destroyed",
                subject=subject,
                value={"instead": actions},
                zones=["battlefield"]
            )
            
            logger.debug(f"[DestructionParser] Created ReplacementEffect: {effect.kind}")
            
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            logger.error(f"[DestructionParser] Error parsing: {e}")
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse destruction replacement: {e}"]
            )

