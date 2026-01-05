# axis2/parsing/continuous_effects/ability_grant.py

from typing import Optional, Union
from .base import ContinuousEffectParser, ParseResult
from .patterns import HAS_ABILITY_RE, GAINS_ABILITY_RE, ABILITY_KEYWORDS
from axis2.schema import ContinuousEffect, GrantedAbility, ParseContext
from axis2.parsing.layers import assign_layer_to_effect
import re
import logging

logger = logging.getLogger(__name__)

# Patterns for parameterized abilities
WARD_PATTERN = re.compile(r"ward\s*\{(\d+)\}", re.IGNORECASE)
WARD_COST_PATTERN = re.compile(
    r"ward\s*(?:—|-)?\s*(\{[^}]+\}|pay\s+(\d+)\s+life|discard\s+(?:a|an|\d+)\s+cards?|sacrifice\s+.*?|collect\s+evidence)",
    re.IGNORECASE
)
PROTECTION_PATTERN = re.compile(r"protection\s+from\s+(.+?)(?:\.|$)", re.IGNORECASE)
ANNIHILATOR_PATTERN = re.compile(r"annihilator\s+(\d+)", re.IGNORECASE)
LANDWALK_PATTERN = re.compile(r"(\w+)\s*walk", re.IGNORECASE)

# Land types for landwalk
LAND_TYPES = {
    "island", "plains", "swamp", "mountain", "forest",
    "snow", "basic", "nonbasic"
}


class AbilityGrantParser(ContinuousEffectParser):
    """Comprehensive parser for ability granting effects: 'has flying', 'gains haste', 'has ward {2}', etc."""
    priority = 50  # Same priority as AbilitiesParser, but more comprehensive
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        """Quick check if this parser might match. Must be CHEAP."""
        lower = text.lower()
        return "has " in lower or "gains " in lower or "gain " in lower or "have " in lower
    
    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        """Parse ability granting text into ContinuousEffect with GrantedAbility list"""
        lower = text.lower()
        logger.warning(f"[AbilityGrantParser] Parsing: {text[:100]}, applies_to={applies_to}")
        
        # Extract the part after "has ...", "gains ...", "gain ...", or "have ..."
        ability_part = None
        if "has " in lower:
            m = HAS_ABILITY_RE.search(lower)
            if m:
                ability_part = m.group(1)
                logger.debug(f"[AbilityGrantParser] Extracted from 'has': {ability_part}")
        elif "gains " in lower or "gain " in lower:
            m = GAINS_ABILITY_RE.search(lower)
            if m:
                ability_part = m.group(1)
                logger.debug(f"[AbilityGrantParser] Extracted from 'gains': {ability_part}")
        elif "have " in lower:
            # Handle "have" (plural form)
            m = re.search(r"have\s+(.+)", lower, re.IGNORECASE)
            if m:
                ability_part = m.group(1)
                logger.debug(f"[AbilityGrantParser] Extracted from 'have': {ability_part}")
        
        if not ability_part:
            logger.warning(f"[AbilityGrantParser] No ability part extracted from: {text[:100]}")
            return ParseResult(matched=False)
        
        # Normalize separators
        ability_part = ability_part.replace(", and ", ", ")
        ability_part = ability_part.replace(" and ", ", ")
        raw = [a.strip().rstrip(".") for a in ability_part.split(",")]
        logger.debug(f"[AbilityGrantParser] Split into raw abilities: {raw}")
        
        abilities: list[GrantedAbility] = []
        
        for a in raw:
            a_clean = re.sub(r"\s+until.*$", "", a).strip().lower()
            logger.warning(f"[AbilityGrantParser] Processing ability: '{a}' -> cleaned: '{a_clean}'")
            
            # Try parameterized abilities first (more specific patterns)
            
            # 1. Ward {N} or Ward with cost
            ward_match = WARD_PATTERN.search(a_clean)
            if ward_match:
                value = int(ward_match.group(1))
                logger.warning(f"[AbilityGrantParser] Found ward {value}")
                abilities.append(GrantedAbility(kind="ward", value=value))
                continue
            
            # Try more complex ward costs (pay life, discard, etc.)
            ward_cost_match = WARD_COST_PATTERN.search(a_clean)
            if ward_cost_match:
                cost_text = ward_cost_match.group(1) or ward_cost_match.group(0)
                # Try to extract numeric value if it's a simple {N}
                numeric_match = re.search(r"\{(\d+)\}", cost_text)
                if numeric_match:
                    value = int(numeric_match.group(1))
                    logger.debug(f"[AbilityGrantParser] Found ward with cost {value}")
                    abilities.append(GrantedAbility(kind="ward", value=value))
                else:
                    # For complex costs, store as string in value (will need schema update)
                    logger.debug(f"[AbilityGrantParser] Found ward with complex cost: {cost_text}")
                    abilities.append(GrantedAbility(kind="ward", value=None))  # Axis3 will parse cost_text
                continue
            
            # 2. Protection from X
            prot_match = PROTECTION_PATTERN.search(a_clean)
            if prot_match:
                protection_value = prot_match.group(1).strip()
                logger.debug(f"[AbilityGrantParser] Found protection from: {protection_value}")
                # Protection is handled by ProtectionParser, but we can also grant it as an ability
                # For now, we'll let ProtectionParser handle it, but we could create GrantedAbility here
                # Note: ProtectionParser uses grant_protection kind, not grant_ability
                # So we skip this here and let ProtectionParser handle it
                continue
            
            # 3. Annihilator N
            annihilator_match = ANNIHILATOR_PATTERN.search(a_clean)
            if annihilator_match:
                value = int(annihilator_match.group(1))
                logger.debug(f"[AbilityGrantParser] Found annihilator {value}")
                abilities.append(GrantedAbility(kind="annihilator", value=value))
                continue
            
            # 4. Landwalk variants
            landwalk_match = LANDWALK_PATTERN.search(a_clean)
            if landwalk_match:
                land_type = landwalk_match.group(1).lower()
                logger.debug(f"[AbilityGrantParser] Found {land_type}walk")
                # Store land type in value as string
                abilities.append(GrantedAbility(kind="landwalk", value=land_type))
                continue
            
            # Simple keyword abilities - check exact match
            if a_clean in ABILITY_KEYWORDS:
                logger.debug(f"[AbilityGrantParser] Found simple ability: {a_clean}")
                abilities.append(GrantedAbility(kind=a_clean))
                continue
            
            # Try matching against keywords - check if ability text contains or matches keyword
            for keyword in ABILITY_KEYWORDS:
                if a_clean == keyword or a_clean.strip() == keyword:
                    logger.debug(f"[AbilityGrantParser] Matched keyword: {keyword}")
                    abilities.append(GrantedAbility(kind=keyword))
                    break
        
        if not abilities:
            logger.debug(f"[AbilityGrantParser] No abilities found")
            return ParseResult(matched=False)
        
        logger.debug(f"[AbilityGrantParser] Created {len(abilities)} granted abilities")
        
        effect = ContinuousEffect(
            kind="grant_ability",
            applies_to=applies_to,
            abilities=abilities,
            condition=condition,
            text=text,
            duration=duration,
            layer=6,  # Will be overridden by assign_layer_to_effect, but set default
        )
        
        # Assign layer and sublayer
        assign_layer_to_effect(effect)
        
        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

