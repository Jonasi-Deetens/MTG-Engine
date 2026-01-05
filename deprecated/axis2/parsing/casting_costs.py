"""
Parsers for special casting costs and alternative costs.

Handles: Flashback, Overload, Kicker, Buyback, Retrace, Rebound,
Suspend, Foretell, Adventure, Prototype, and other special casting mechanics.
"""

import re
from typing import List, Optional
from axis2.schema import CastingOption, ManaCost, ParseContext
from axis2.parsing.mana import parse_mana_cost


# Regex patterns for each casting cost type
FLASHBACK_RE = re.compile(r"flashback\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
OVERLOAD_RE = re.compile(r"overload\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
KICKER_RE = re.compile(r"kicker\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
BUYBACK_RE = re.compile(r"buyback\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
RETRACE_RE = re.compile(r"retrace", re.IGNORECASE)
REBOUND_RE = re.compile(r"rebound", re.IGNORECASE)
SUSPEND_RE = re.compile(r"suspend\s+(\d+)\s*—\s*(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
FORETELL_RE = re.compile(r"foretell\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
ADVENTURE_RE = re.compile(r"adventure\s+—\s*(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
PROTOTYPE_RE = re.compile(r"prototype\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)\s+(\d+)/(\d+)", re.IGNORECASE)
BESTOW_RE = re.compile(r"bestow\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
MORPH_RE = re.compile(r"morph\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
MANIFEST_RE = re.compile(r"manifest", re.IGNORECASE)
MUTATE_RE = re.compile(r"mutate\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
DISTURB_RE = re.compile(r"disturb\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
EMERGE_RE = re.compile(r"emerge\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
EVOKE_RE = re.compile(r"evoke\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
CYCLING_RE = re.compile(r"cycling\s+(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)
CHANNEL_RE = re.compile(r"channel\s+—\s*(\{[^}]+\}(?:\s*\{[^}]+\})*)", re.IGNORECASE)


def _extract_mana_symbols(cost_text: str) -> List[str]:
    """Extract mana symbols from cost text like '{1}{R}{G}'."""
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
    return symbols


def parse_flashback_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Flashback cost.
    Example: "Flashback {3}{R}"
    """
    m = FLASHBACK_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="flashback",
        mana_cost=mana_cost,
        additional_costs=[]  # Flashback may exile from graveyard, handled separately
    )


def parse_overload_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Overload cost.
    Example: "Overload {5}{U}{R}"
    """
    m = OVERLOAD_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="overload",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_kicker_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Kicker cost.
    Example: "Kicker {1}{R}"
    Note: Kicker is an additional cost, not an alternative cost.
    """
    m = KICKER_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="kicker",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_buyback_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Buyback cost.
    Example: "Buyback {3}"
    """
    m = BUYBACK_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="buyback",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_retrace_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Retrace.
    Example: "Retrace"
    Note: Retrace allows casting from graveyard by discarding a land.
    """
    if not RETRACE_RE.search(text):
        return None
    
    return CastingOption(
        kind="retrace",
        mana_cost=None,  # Uses original mana cost
        additional_costs=[]  # Discard land is handled separately
    )


def parse_rebound_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Rebound.
    Example: "Rebound"
    Note: Rebound is not a cost, but a delayed trigger. However, we track it as a casting option.
    """
    if not REBOUND_RE.search(text):
        return None
    
    return CastingOption(
        kind="rebound",
        mana_cost=None,
        additional_costs=[]
    )


def parse_suspend_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Suspend cost.
    Example: "Suspend 3—{1}{R}"
    """
    m = SUSPEND_RE.search(text)
    if not m:
        return None
    
    time_counters = int(m.group(1))
    cost_text = m.group(2)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="suspend",
        mana_cost=mana_cost,
        additional_costs=[{"time_counters": time_counters}]
    )


def parse_foretell_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Foretell cost.
    Example: "Foretell {1}{R}"
    """
    m = FORETELL_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="foretell",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_adventure_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Adventure cost.
    Example: "Adventure — {1}{R} Sorcery"
    Note: Adventure is a special spell type, not just a cost.
    """
    m = ADVENTURE_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="adventure",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_prototype_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Prototype cost.
    Example: "Prototype {3} 2/3"
    Note: Prototype includes P/T values.
    """
    m = PROTOTYPE_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    power = int(m.group(2))
    toughness = int(m.group(3))
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="prototype",
        mana_cost=mana_cost,
        additional_costs=[{"power": power, "toughness": toughness}]
    )


def parse_bestow_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Bestow cost.
    Example: "Bestow {3}{W}"
    """
    m = BESTOW_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="bestow",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_morph_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Morph cost.
    Example: "Morph {3}"
    """
    m = MORPH_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="morph",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_manifest_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Manifest (no cost, just keyword).
    Example: "Manifest"
    """
    if not MANIFEST_RE.search(text):
        return None
    
    return CastingOption(
        kind="manifest",
        mana_cost=None,
        additional_costs=[]
    )


def parse_mutate_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Mutate cost.
    Example: "Mutate {3}{G}"
    """
    m = MUTATE_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="mutate",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_disturb_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Disturb cost.
    Example: "Disturb {2}{U}"
    """
    m = DISTURB_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="disturb",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_emerge_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Emerge cost.
    Example: "Emerge {5}{B}"
    """
    m = EMERGE_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="emerge",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_evoke_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Evoke cost.
    Example: "Evoke {1}{U}"
    """
    m = EVOKE_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="evoke",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_cycling_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Cycling cost (as casting cost alternative).
    Example: "Cycling {2}"
    """
    m = CYCLING_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="cycling",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_channel_cost(text: str) -> Optional[CastingOption]:
    """
    Parse Channel cost.
    Example: "Channel — {2}{R}"
    """
    m = CHANNEL_RE.search(text)
    if not m:
        return None
    
    cost_text = m.group(1)
    symbols = _extract_mana_symbols(cost_text)
    mana_cost = ManaCost(symbols=symbols)
    
    return CastingOption(
        kind="channel",
        mana_cost=mana_cost,
        additional_costs=[]
    )


def parse_all_casting_costs(text: str, ctx: ParseContext) -> List[CastingOption]:
    """
    Parse all special casting costs from text.
    
    Returns a list of CastingOption objects for all detected special costs.
    """
    costs = []
    
    # Try each parser in order
    parsers = [
        parse_flashback_cost,
        parse_overload_cost,
        parse_kicker_cost,
        parse_buyback_cost,
        parse_retrace_cost,
        parse_rebound_cost,
        parse_suspend_cost,
        parse_foretell_cost,
        parse_adventure_cost,
        parse_prototype_cost,
        parse_bestow_cost,
        parse_morph_cost,
        parse_manifest_cost,
        parse_mutate_cost,
        parse_disturb_cost,
        parse_emerge_cost,
        parse_evoke_cost,
        parse_cycling_cost,
        parse_channel_cost,
    ]
    
    for parser in parsers:
        result = parser(text)
        if result:
            costs.append(result)
    
    return costs

