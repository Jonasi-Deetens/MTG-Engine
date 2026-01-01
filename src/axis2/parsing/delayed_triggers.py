import re
from typing import Optional
from axis2.schema import (
    TriggeredAbility,
    ChangeZoneEffect,
    Subject,
)
from axis2.parsing.sentences import split_into_sentences
from axis2.parsing.triggers import LeavesBattlefieldEvent  # adjust import to your actual location


UNTIL_LEAVES_RE = re.compile(
    r"until\s+(this creature|this permanent|it|that creature|that permanent)\s+leaves the battlefield",
    re.IGNORECASE,
)

def has_until_leaves_clause(effect_text: str) -> bool:
    if not effect_text:
        return False
    text = effect_text.lower()
    return UNTIL_LEAVES_RE.search(text) is not None


def build_linked_return_trigger(etb_trigger: TriggeredAbility) -> Optional[TriggeredAbility]:
    """
    If the given ETB trigger exiles a target, synthesize a linked LTB trigger:
      'When this leaves the battlefield, return the exiled card to the battlefield.'
    Returns a new TriggeredAbility or None if not applicable.
    """
    exile_effect: Optional[ChangeZoneEffect] = None

    for eff in etb_trigger.effects:
        if isinstance(eff, ChangeZoneEffect) and eff.to_zone == "exile":
            exile_effect = eff
            break

    if exile_effect is None:
        return None

    # This is the linked-return pattern: we don't target again,
    # we reference "the card exiled with this".
    return TriggeredAbility(
        event=LeavesBattlefieldEvent(subject="this permanent"),
        condition_text="When this permanent leaves the battlefield",
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
