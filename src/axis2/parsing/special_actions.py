import re
from axis2.schema import SpecialAction, ManaCost, AddCountersEffect, Subject, ParseContext
from axis2.parsing.subject import subject_from_text
from axis2.parsing.continuous_effects import NUMBER_WORDS

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

COUNTER_RE = re.compile(
    r"put\s+(?P<count>that many|\w+)\s+(?P<counter_type>[\w\+\-\/]+)\s+counters?\s+on\s+(?P<subject>[^\.]+)",
    re.IGNORECASE
)

def extract_counter_instruction(sentence: str):
    """
    Extracts counter type and count expression from sentences like:
      'put that many valor counters on this creature'
      'put two +1/+1 counters on target creature'
    Returns (counter_type, count_expr, subject_text) or None.
    """
    m = COUNTER_RE.search(sentence)
    if not m:
        return None

    raw_count = m.group("count").lower().strip()
    raw_type = m.group("counter_type").lower().strip()
    raw_subject = m.group("subject").strip()

    # Normalize count
    if raw_count == "that many":
        count_expr = "that_many"
    elif raw_count.isdigit():
        count_expr = int(raw_count)
    else:
        # number words like "two", "three"
        NUMBER_WORDS = {
            "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10
        }
        count_expr = NUMBER_WORDS.get(raw_count, raw_count)

    return raw_type, count_expr, raw_subject


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
    if not oracle_text:
        return None

    m = REPEATABLE_PAYMENT_RE.search(oracle_text)
    if not m:
        return None

    # Parse mana cost
    cost_text = m.group("cost")
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

    # ------------------------------------------------------------
    # NEW: detect counter type from the next sentence
    # ------------------------------------------------------------
    counter_type = "dynamic"
    for sentence in oracle_text.split("."):
        extracted = extract_counter_instruction(sentence)
        if extracted:
            counter_type, count_expr, subj_text = extracted
            break

    # count_expr for Intrepid Adversary = "that_many"
    # but we want "times_paid" for the SpecialAction
    count_expr = "times_paid"

    effect = AddCountersEffect(
        counter_type=counter_type,
        count=count_expr,
        subject=subject_from_text(ctx.card_name, ctx)
    )

    return SpecialAction(
        name="RepeatablePayment",
        cost=cost,
        conditions=["etb_window"],
        effects=[effect],
        kind="repeatable_payment"
    )
