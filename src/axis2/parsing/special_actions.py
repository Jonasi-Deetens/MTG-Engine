import re
from axis2.schema import SpecialAction, ManaCost, AddCountersEffect, Subject, ParseContext
from axis2.parsing.subject import subject_from_text

NINJUTSU_RE = re.compile(r"ninjutsu\s+(\{[^}]+\})", re.IGNORECASE)

def parse_ninjutsu(oracle_text: str):
    """
    Detects and parses Ninjutsu keyword into a SpecialAction.
    Example:
        'Ninjutsu {1}{U}' → SpecialAction(...)
    """
    if not oracle_text:
        return None

    m = NINJUTSU_RE.search(oracle_text)
    if not m:
        return None

    cost_text = m.group(1)

    # Parse mana cost symbols
    symbols = []
    buf = ""
    inside = False
    for ch in cost_text:
        if ch == "{":
            inside = True
            buf = "{"
        elif ch == "}":
            inside = False
            buf += "}"
            symbols.append(buf)
            buf = ""
        elif inside:
            buf += ch

    cost = ManaCost(symbols=symbols)

    # Semantic meaning of Ninjutsu
    conditions = [
        "you_control_unblocked_attacker",
        "card_in_hand",
    ]

    effects = [
        {
            "type": "put_onto_battlefield_tapped_and_attacking",
            "subject": "this",
            "origin": "hand",
        }
    ]

    return SpecialAction(
        name="Ninjutsu",
        cost=cost,
        conditions=conditions,
        effects=effects,
    )

REPEATABLE_PAYMENT_RE = re.compile(
    r"you may pay\s+(?P<cost>(\{[^}]+\})+)\s+any number of times",
    re.IGNORECASE
)

def parse_repeatable_payment(oracle_text: str, ctx: ParseContext):
    """
    Detects patterns like:
        'you may pay {1}{W} any number of times'
    and converts them into a repeatable-payment SpecialAction.
    """
    if not oracle_text:
        return None

    m = REPEATABLE_PAYMENT_RE.search(oracle_text)
    if not m:
        return None

    cost_text = m.group("cost")

    # Parse mana symbols (same logic as Ninjutsu)
    symbols = []
    buf = ""
    inside = False
    for ch in cost_text:
        if ch == "{":
            inside = True
            buf = "{"
        elif ch == "}":
            inside = False
            buf += "}"
            symbols.append(buf)
            buf = ""
        elif inside:
            buf += ch

    cost = ManaCost(symbols=symbols)

    # Semantic meaning:
    # Axis3 will interpret "times_paid" dynamically.
    effects = [
        {
            "type": "add_counters",
            "counter_type": "dynamic",   # Axis3 will refine this
            "count": "times_paid",
            "subject": "this",
        }
    ]

    return SpecialAction(
        name="RepeatablePayment",
        cost=cost,
        conditions=["etb_window"],
        effects=[
            AddCountersEffect(
                counter_type="dynamic",   # Axis3 will refine this to "valor"
                count="times_paid",
                subject=subject_from_text(ctx.card_name, ctx)
            )
        ],
        kind="repeatable_payment",
    )
