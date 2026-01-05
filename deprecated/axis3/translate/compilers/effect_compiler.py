import re

# ------------------------------------------------------------
# Axis3 effect classes
# ------------------------------------------------------------
from axis3.engine.abilities.effects.damage import DealDamageEffect
from axis3.engine.abilities.effects.draw import DrawCardEffect
from axis3.engine.abilities.effects.create_token import (
    CreateTokenEffect,
    CreateDynamicTokenEffect,
)
from axis3.engine.abilities.effects.gain_life import GainLifeEffect
from axis3.engine.abilities.effects.put_counters import PutCountersEffect
from axis3.engine.abilities.effects.unparsed import UnparsedEffect
from axis3.engine.abilities.effects.mana import AddManaEffect
from axis3.engine.abilities.effects.destroy import DestroyEffect
from axis3.engine.abilities.effects.exile import ExileEffect
from axis3.engine.abilities.effects.bounce import BounceEffect
from axis3.engine.abilities.effects.scry import ScryEffect
from axis3.engine.abilities.effects.mill import MillEffect
from axis3.engine.abilities.effects.fight import FightEffect
from axis3.engine.abilities.effects.gain_control import GainControlEffect
from axis3.engine.abilities.effects.tap import TapEffect
from axis3.engine.abilities.effects.untap import UntapEffect
from axis3.engine.abilities.effects.search import SearchLibraryEffect
from axis3.engine.abilities.effects.reveal import RevealEffect
from axis3.engine.abilities.effects.life_loss import LoseLifeEffect
from axis3.engine.abilities.effects.return_from_graveyard import ReturnFromGYEffect
from axis3.engine.abilities.effects.create_emblem import CreateEmblemEffect
from axis3.engine.abilities.effects.add_keyword import AddKeywordEffect
from axis3.engine.abilities.effects.remove_keyword import RemoveKeywordEffect
from axis3.engine.abilities.effects.flashback import FlashbackEffect


# ------------------------------------------------------------
# Target parsing → Axis3 subject resolver keys
# ------------------------------------------------------------

def parse_target(text: str) -> str:
    t = text.strip().lower()

    if t in ("any target", "any"):
        return "any"

    if "target creature" in t:
        return "target_creature"

    if "target player" in t:
        return "target_player"

    if "target opponent" in t:
        return "target_opponent"

    if "target artifact" in t:
        return "target_artifact"

    if "target enchantment" in t:
        return "target_enchantment"

    if "target permanent" in t:
        return "target_permanent"

    if "each opponent" in t:
        return "each_opponent"

    if "each creature" in t:
        return "each_creature"

    return t


# ------------------------------------------------------------
# Sub‑parsers for each effect type (Axis3‑style)
# ------------------------------------------------------------

FLASHBACK_PATTERN = re.compile(
    r"flashback\s+(?P<cost>\{[^}]+\}(?:\{[^}]+\})*)",
    re.IGNORECASE,
)


def parse_flashback(text: str):
    m = FLASHBACK_PATTERN.search(text)
    if not m:
        return None

    cost = m.group("cost")
    reduction = (
        "greatest_commander_mv"
        if "greatest mana value of a commander" in text
        else None
    )

    return FlashbackEffect(
        flashback_cost=cost,
        reduction_source=reduction,
    )


DYNAMIC_TOKEN_PATTERN = re.compile(
    r"create\s+a\s+1/1\s+(?P<color>\w+)\s+(?P<subtype>\w+)\s+creature\s+token\s+for\s+each\s+(?P<subject>[\w\s]+)",
    re.IGNORECASE,
)


def parse_dynamic_token_effect(text: str):
    m = DYNAMIC_TOKEN_PATTERN.search(text)
    if not m:
        return None

    color = m.group("color").lower()
    subtype = m.group("subtype").lower()
    subject = m.group("subject").strip().lower()

    return CreateDynamicTokenEffect(
        power=1,
        toughness=1,
        colors=[color],
        types=["Creature"],
        subtypes=[subtype],
        count_source=subject,
    )


def parse_mana_effect(text: str):
    """
    Very simple: count {W}{U}{B}{R}{G} and build AddManaEffect(color=...).
    """
    effects = []
    upper = text.upper()

    for c in "WUBRG":
        token = f"{{{c}}}"
        count = upper.count(token)
        for _ in range(count):
            effects.append(AddManaEffect(color=c))

    return effects


def parse_damage_effect(text: str):
    m = re.search(r"deal\s+(\d+)\s+damage\s+to\s+(.+)", text, re.IGNORECASE)
    if not m:
        return None

    amount = int(m.group(1))
    target = parse_target(m.group(2))

    return DealDamageEffect(
        amount=amount,
        subject=target,
    )


def parse_draw_effect(text: str):
    m = re.search(r"draw\s+(\d+)\s+cards?", text, re.IGNORECASE)
    if m:
        amount = int(m.group(1))
        return DrawCardEffect(amount=amount)
    return None


def parse_token_effect(text: str):
    m = re.search(r"create\s+(\d+)\s+(\d+)/(\d+)\s+(\w+)\s+tokens?", text, re.IGNORECASE)
    if not m:
        return None

    count = int(m.group(1))
    power = int(m.group(2))
    toughness = int(m.group(3))
    creature_type = m.group(4)

    return CreateTokenEffect(
        token_name=f"{power}/{toughness} {creature_type} token",
        power=power,
        toughness=toughness,
        colors=None,
        types=["Creature"],
        subtypes=[creature_type],
        count=count,
    )


def parse_gain_life(text: str):
    m = re.search(r"you\s+gain\s+(\d+)\s+life", text, re.IGNORECASE)
    if m:
        amount = int(m.group(1))
        return GainLifeEffect(amount=amount)
    return None


def parse_counters(text: str):
    m = re.search(r"put\s+(\d+)\s+\+1/\+1\s+counters?\s+on\s+(.+)", text, re.IGNORECASE)
    if not m:
        return None

    count = int(m.group(1))
    target = parse_target(m.group(2))

    return PutCountersEffect(
        amount=count,
        subject=target,
        counter_type="+1/+1",
    )


def parse_destroy(text: str):
    m = re.search(r"destroy\s+target\s+(.+)", text, re.IGNORECASE)
    if m:
        target = parse_target("target " + m.group(1))
        return DestroyEffect(subject=target)
    return None


def parse_exile(text: str):
    m = re.search(r"exile\s+target\s+(.+)", text, re.IGNORECASE)
    if m:
        target = parse_target("target " + m.group(1))
        return ExileEffect(subject=target)
    return None


def parse_bounce(text: str):
    m = re.search(
        r"return\s+target\s+(.+)\s+to\s+its\s+owner'?s\s+hand",
        text,
        re.IGNORECASE,
    )
    if m:
        target = parse_target("target " + m.group(1))
        return BounceEffect(subject=target)
    return None


def parse_scry(text: str):
    m = re.search(r"scry\s+(\d+)", text, re.IGNORECASE)
    if m:
        amount = int(m.group(1))
        return ScryEffect(amount=amount)
    return None


def parse_mill(text: str):
    m = re.search(r"mill\s+(\d+)", text, re.IGNORECASE)
    if m:
        amount = int(m.group(1))
        # default subject: target player (your old pattern)
        return MillEffect(amount=amount, subject="target_player")
    return None


def parse_fight(text: str):
    if "fight" in text.lower():
        # rely on effect to interpret "self fights target_creature"
        return FightEffect()
    return None


def parse_lose_life(text: str):
    m = re.search(r"target\s+player\s+loses\s+(\d+)\s+life", text, re.IGNORECASE)
    if m:
        amount = int(m.group(1))
        return LoseLifeEffect(amount=amount, subject="target_player")
    return None


def parse_return_from_gy(text: str):
    m = re.search(
        r"return\s+target\s+(.+)\s+from\s+your\s+graveyard\s+to\s+(.+)",
        text,
        re.IGNORECASE,
    )
    if m:
        target = parse_target("target " + m.group(1))
        destination = m.group(2).strip().lower()  # "your hand", "the battlefield", etc.
        return ReturnFromGYEffect(
            subject=target,
            destination=destination,
        )
    return None


def parse_gain_control(text: str):
    m = re.search(r"gain\s+control\s+of\s+target\s+(.+)", text, re.IGNORECASE)
    if m:
        target = parse_target("target " + m.group(1))
        return GainControlEffect(subject=target)
    return None


def parse_tap(text: str):
    m = re.search(r"tap\s+target\s+(.+)", text, re.IGNORECASE)
    if m:
        target = parse_target("target " + m.group(1))
        return TapEffect(subject=target)
    return None


def parse_untap(text: str):
    m = re.search(r"untap\s+target\s+(.+)", text, re.IGNORECASE)
    if m:
        target = parse_target("target " + m.group(1))
        return UntapEffect(subject=target)
    return None


# (SearchLibraryEffect, RevealEffect, CreateEmblemEffect, AddKeywordEffect,
#  RemoveKeywordEffect can be added later when you have clear patterns.)


# ------------------------------------------------------------
# Main compiler
# ------------------------------------------------------------

def compile_effect(effect_text: str):
    """
    Compile a single rules text line into one Axis3Effect.
    """
    text = effect_text.strip()

    lower = text.lower()

    # 1. Mana
    if lower.startswith("add"):
        effects = parse_mana_effect(text)
        if effects:
            # For now, assume a single AddManaEffect or a list of identical ones.
            # Caller can handle multiple if needed.
            return effects[0] if len(effects) == 1 else effects

    # 2. Damage
    eff = parse_damage_effect(text)
    if eff:
        return eff

    # 3. Draw
    eff = parse_draw_effect(text)
    if eff:
        return eff

    # 4. Dynamic tokens
    eff = parse_dynamic_token_effect(text)
    if eff:
        return eff

    # 5. Fixed tokens
    eff = parse_token_effect(text)
    if eff:
        return eff

    # 6. Gain life
    eff = parse_gain_life(text)
    if eff:
        return eff

    # 7. Counters
    eff = parse_counters(text)
    if eff:
        return eff

    # 8. Destroy
    eff = parse_destroy(text)
    if eff:
        return eff

    # 9. Exile
    eff = parse_exile(text)
    if eff:
        return eff

    # 10. Bounce
    eff = parse_bounce(text)
    if eff:
        return eff

    # 11. Scry
    eff = parse_scry(text)
    if eff:
        return eff

    # 12. Mill
    eff = parse_mill(text)
    if eff:
        return eff

    # 13. Fight
    eff = parse_fight(text)
    if eff:
        return eff

    # 14. Lose life
    eff = parse_lose_life(text)
    if eff:
        return eff

    # 15. Return from GY
    eff = parse_return_from_gy(text)
    if eff:
        return eff

    # 16. Gain control
    eff = parse_gain_control(text)
    if eff:
        return eff

    # 17. Tap / Untap
    eff = parse_tap(text)
    if eff:
        return eff

    eff = parse_untap(text)
    if eff:
        return eff

    # 18. Flashback
    eff = parse_flashback(text)
    if eff:
        return eff

    # Fallback
    return UnparsedEffect(raw=effect_text)
