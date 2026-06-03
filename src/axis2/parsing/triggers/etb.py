# axis2/parsing/triggers/etb.py

from .base import TriggerParser, ParseResult
from .patterns import ETB_RE
from axis2.schema import EntersBattlefieldEvent

class ETBParser(TriggerParser):
    """Parses enters-the-battlefield triggers: 'when X enters the battlefield'"""
    priority = 40  # Medium priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "enters" in text.lower() and ("when" in text.lower() or "whenever" in text.lower())

    def parse(self, text: str) -> ParseResult:
        m = ETB_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            subject_text = m.group(1).strip()
            
            # Normalize common self-reference patterns
            subject_lower = subject_text.lower()
            if subject_lower in ["this", "this permanent", "this creature", "this enchantment", 
                                 "this artifact", "this spell", "this aura", "this equipment"]:
                normalized_subject = "self"
            elif "this" in subject_lower:
                # "this Aura" -> "self", but preserve type info if needed
                normalized_subject = "self"
            else:
                # Check if it looks like a card name (capitalized, multiple words, not a common pattern)
                # For now, keep as-is - normalization will happen in builder with card_name context
                normalized_subject = subject_text
            
            event = EntersBattlefieldEvent(subject=normalized_subject)

            return ParseResult(
                matched=True,
                event=event
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse ETB trigger: {e}"]
            )

