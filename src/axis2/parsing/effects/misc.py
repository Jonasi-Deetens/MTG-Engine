# axis2/parsing/effects/misc.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import (
    ScryEffect, SurveilEffect, RevealEffect, CounterSpellEffect,
    ReturnCardFromGraveyardEffect, DraftFromSpellbookEffect, PTBoostEffect,
    ShuffleEffect, Subject, EquipEffect, ParseContext
)

SCRY_RE = re.compile(r"\bscry\s+(\d+)\b", re.IGNORECASE)

SURVEIL_RE = re.compile(r"\bsurveil\s+(\d+)\b", re.IGNORECASE)

REVEAL_THOSE_RE = re.compile(
    r"reveal those cards",
    re.IGNORECASE
)

COUNTER_SPELL_RE = re.compile(
    r"counter (target )?spell",
    re.IGNORECASE
)

RETURN_CARD_RE = re.compile(
    r"return (?:up to )?target ([a-z ]+?) card from (?:your|an opponent's|a|their) graveyard to (?:your|its owner's|their) ([a-z ]+)",
    re.IGNORECASE
)

SPELLBOOK_RE = re.compile(
    r"draft a card from ([a-zA-Z ]+)'s spellbook",
    re.IGNORECASE
)

# Pattern for P/T modifications: "gets +3/+3", "gets -X/-X", etc.
# Matches: "gets +3/+3", "gets -X/-X", "gets +1/+1"
PT_BOOST_RE = re.compile(
    r"gets\s+([+\-]?\w+)\/([+\-]?\w+)",
    re.IGNORECASE
)

# Pattern for dynamic value clauses: "where X is the number of..."
DYNAMIC_VALUE_RE = re.compile(
    r"where\s+(\w+)\s+is\s+(?:the\s+number\s+of|equal\s+to)\s+(.+?)(?:\.|$)",
    re.IGNORECASE
)

SHUFFLE_RE = re.compile(r"shuffle", re.IGNORECASE)

class ScryParser(EffectParser):
    """Parses scry effects"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "scry" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = SCRY_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        return ParseResult(
            matched=True,
            effect=ScryEffect(amount=int(m.group(1))),
            consumed_text=text
        )

class SurveilParser(EffectParser):
    """Parses surveil effects"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "surveil" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = SURVEIL_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        return ParseResult(
            matched=True,
            effect=SurveilEffect(amount=int(m.group(1))),
            consumed_text=text
        )

class RevealThoseParser(EffectParser):
    """Parses 'reveal those cards' effects"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "reveal those" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if REVEAL_THOSE_RE.search(text):
            return ParseResult(
                matched=True,
                effect=RevealEffect(subject=Subject(scope="searched_cards")),
                consumed_text=text
            )
        return ParseResult(matched=False)

class CounterSpellParser(EffectParser):
    """Parses counter spell effects"""
    priority = 50
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "counter" in text.lower() and "spell" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if COUNTER_SPELL_RE.search(text):
            return ParseResult(
                matched=True,
                effect=CounterSpellEffect(target="target_spell"),
                consumed_text=text
            )
        return ParseResult(matched=False)

class ReturnCardParser(EffectParser):
    """Parses return card from graveyard effects"""
    priority = 40
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "return" in text.lower() and "graveyard" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = RETURN_CARD_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        subtype = m.group(1).strip()
        dest_zone = m.group(2).strip()

        # normalize destination zone
        zone_map = {
            "hand": "hand",
            "battlefield": "battlefield",
            "battlefield tapped": "battlefield_tapped",
            "command zone": "command_zone",
        }
        dest_zone = zone_map.get(dest_zone, dest_zone)

        return ParseResult(
            matched=True,
            effect=ReturnCardFromGraveyardEffect(
                subtype=subtype,
                controller="you",
                destination_zone=dest_zone
            ),
            consumed_text=text
        )

class SpellbookParser(EffectParser):
    """Parses spellbook draft effects"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "spellbook" in text.lower() and "draft" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = SPELLBOOK_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        return ParseResult(
            matched=True,
            effect=DraftFromSpellbookEffect(source=m.group(1).strip()),
            consumed_text=text
        )

class PTBoostParser(EffectParser):
    """
    Parses P/T modification effects: 
    - 'target creature gets +3/+3 until end of turn'
    - 'target creature an opponent controls gets -X/-X until end of turn, where X is...'
    """
    priority = 50
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        text_lower = text.lower()
        return "gets" in text_lower and "/" in text_lower
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        from axis2.schema import ContinuousEffect, PTExpression, DynamicValue
        from axis2.parsing.subject import subject_from_text
        from axis2.parsing.layers import assign_layer_to_effect
        
        m = PT_BOOST_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        
        try:
            power_str = m.group(1).strip()
            toughness_str = m.group(2).strip()
            
            # Check if this is a numeric value or a variable (X, *, etc.)
            try:
                power = int(power_str)
                toughness = int(toughness_str)
                # Simple numeric boost - use PTBoostEffect
                return ParseResult(
                    matched=True,
                    effect=PTBoostEffect(power=power, toughness=toughness),
                    consumed_text=text
                )
            except ValueError:
                # Variable or expression (X, *, etc.) - use ContinuousEffect
                pt = PTExpression(power=power_str, toughness=toughness_str)
                
                # Extract subject from text
                subject = None
                if "target creature" in text.lower():
                    # Try to extract the full subject phrase
                    subject_text = "target creature"
                    if "an opponent controls" in text.lower() or "a player controls" in text.lower():
                        subject_text = "target creature an opponent controls"
                    subject = subject_from_text(subject_text, ctx)
                
                # Detect duration
                duration = None
                if "until end of turn" in text.lower():
                    duration = "until_end_of_turn"
                elif "this turn" in text.lower():
                    duration = "this_turn"
                
                # Detect dynamic value clause
                dynamic = None
                dynamic_m = DYNAMIC_VALUE_RE.search(text)
                if dynamic_m:
                    var_name = dynamic_m.group(1)  # e.g., "X"
                    description = dynamic_m.group(2).strip()  # e.g., "the number of permanent cards in your graveyard"
                    
                    # Parse the description to create a DynamicValue
                    # For "the number of permanent cards in your graveyard"
                    if "permanent" in description.lower() and "graveyard" in description.lower():
                        dynamic = DynamicValue(
                            kind="graveyard_count",
                            counter_type=None,
                            subject=Subject(scope="you", types=["permanent"], filters={"zone": "graveyard"})
                        )
                    # TODO: Parse more complex descriptions
                
                effect = ContinuousEffect(
                    kind="pt_mod",
                    text=text,
                    layer=7,
                    sublayer="7c",
                    applies_to=subject,
                    pt_value=pt,
                    duration=duration,
                    dynamic=dynamic,
                    source_kind="triggered_ability"
                )
                
                # Assign layer and sublayer
                assign_layer_to_effect(effect)
                
                return ParseResult(
                    matched=True,
                    effect=effect,
                    consumed_text=text
                )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=False,
                errors=[f"Failed to parse P/T modification: {e}"]
            )

class ShuffleParser(EffectParser):
    """Parses shuffle effects"""
    priority = 20  # Low priority, very generic
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "shuffle" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if SHUFFLE_RE.search(text):
            return ParseResult(
                matched=True,
                effect=ShuffleEffect(subject=Subject(scope="you")),
                consumed_text=text
            )
        return ParseResult(matched=False)

class EquipParser(EffectParser):
    """Parses Equip keyword ability"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return text.strip().lower().startswith("equip")
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if text.strip().lower().startswith("equip"):
            return ParseResult(
                matched=True,
                effect=EquipEffect(),
                consumed_text=text
            )
        return ParseResult(matched=False)

