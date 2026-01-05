import re
from typing import Optional
from axis2.schema import TriggeredAbility, ChangeZoneEffect, Subject, LeavesBattlefieldEvent

UNTIL_LEAVES_RE = re.compile(
    r"until\s+(?:this|that|the)\s+(?:[a-zA-Z ]+?)?\s*leaves\s+the\s+battlefield",
    re.I
)

def has_until_leaves_clause(oracle_text: str) -> bool:
    return bool(UNTIL_LEAVES_RE.search(oracle_text.lower()))

def build_linked_return_trigger(etb_trigger: TriggeredAbility) -> Optional[TriggeredAbility]:
    # Find the exile effect
    exile_effect = None
    for eff in etb_trigger.effects:
        if isinstance(eff, ChangeZoneEffect) and eff.to_zone == "exile":
            exile_effect = eff
            break

    if exile_effect is None:
        return None

    # Check if event is None (parsing failed)
    if etb_trigger.event is None:
        return None

    # Infer card type from ETB subject ("this enchantment", "this aura", etc.)
    # Handle both event objects with .subject and string events
    if hasattr(etb_trigger.event, 'subject'):
        subject_words = etb_trigger.event.subject.split()
        card_type = subject_words[-1] if subject_words else "permanent"
    else:
        # Fallback: try to extract from condition_text
        condition = etb_trigger.condition_text.lower()
        if "aura" in condition:
            card_type = "aura"
        elif "enchantment" in condition:
            card_type = "enchantment"
        elif "creature" in condition:
            card_type = "creature"
        else:
            card_type = "permanent"

    return TriggeredAbility(
        event=LeavesBattlefieldEvent(subject=f"this {card_type}"),
        condition_text=f"When this {card_type} leaves the battlefield",
        effects=[
            ChangeZoneEffect(
                subject=Subject(
                    scope="linked_exiled_card",
                    filters={"source": "self"},
                ),
                to_zone="battlefield",
            )
        ],
        targeting=None,
        trigger_filter=None,
    )
