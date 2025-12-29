import re

# ------------------------------------------------------------
# Effect classes (your existing Axis3 effects)
# ------------------------------------------------------------
from axis3.engine.abilities.effects.damage import DealDamageEffect
from axis3.engine.abilities.effects.draw import DrawCardEffect
from axis3.engine.abilities.effects.create_token import CreateTokenEffect
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
from axis3.engine.abilities.effects.create_token import CreateDynamicTokenEffect
from axis3.engine.abilities.effects.flashback import FlashbackEffect


# ------------------------------------------------------------
# Target parsing
# ------------------------------------------------------------
def parse_target(text: str):
    text = text.strip().lower()

    if text in ("any target", "any"):
        return "any"

    if "target creature" in text:
        return "creature"

    if "target player" in text:
        return "player"

    if "target opponent" in text:
        return "opponent"

    if "target artifact" in text:
        return "artifact"

    if "target enchantment" in text:
        return "enchantment"

    if "target permanent" in text:
        return "permanent"

    if "each opponent" in text:
        return "each_opponent"

    if "each creature" in text:
        return "each_creature"

    return text


# ------------------------------------------------------------
# Sub‑parsers for each effect type (Axis3‑compatible)
# ------------------------------------------------------------

FLASHBACK_PATTERN = re.compile(
    r"flashback\s+(?P<cost>\{[^}]+\}(?:\{[^}]+\})*)",
    re.IGNORECASE
)

def parse_flashback(text: str):
    m = FLASHBACK_PATTERN.search(text)
    if not m:
        return None

    cost = m.group("cost")

    # Detect commander-based reduction
    reduction = "greatest_commander_mv" if "greatest mana value of a commander" in text else None

    return FlashbackEffect(
        flashback_cost=cost,
        reduction_source=reduction,
    )


DYNAMIC_TOKEN_PATTERN = re.compile(
    r"create\s+a\s+1/1\s+(?P<color>\w+)\s+(?P<subtype>\w+)\s+creature\s+token\s+for\s+each\s+(?P<subject>[\w\s]+)",
    re.IGNORECASE
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
        types=["creature"],
        subtypes=[subtype],
        count_source=subject,
    )



def parse_mana_effect(text: str):
    effects = []
    upper = text.upper()

    for c in "WUBRG":
        token = f"{{{c}}}"
        count = upper.count(token)
        for _ in range(count):
            effects.append(
                AddManaEffect(
                    selector="add_mana",
                    subject="controller",
                    params={"color": c},
                    raw=text,
                )
            )
    return effects


def parse_damage_effect(text: str):
    m = re.search(r"deal\s+(\d+)\s+damage\s+to\s+(.+)", text)
    if not m:
        return None

    amount = int(m.group(1))
    target = parse_target(m.group(2))

    return DealDamageEffect(
        selector="deal_damage",
        subject="target",
        params={"amount": amount, "target": target},
        raw=text,
    )


def parse_draw_effect(text: str):
    m = re.search(r"draw\s+(\d+)\s+cards?", text)
    if m:
        return DrawCardEffect(
            selector="draw",
            subject="controller",
            params={"amount": int(m.group(1))},
            raw=text,
        )
    return None


def parse_token_effect(text: str):
    m = re.search(r"create\s+(\d+)\s+(\d+)/(\d+)\s+(\w+)\s+tokens?", text)
    if not m:
        return None

    count = int(m.group(1))
    power = int(m.group(2))
    toughness = int(m.group(3))
    creature_type = m.group(4)

    return CreateTokenEffect(
        selector="create_token",
        subject="controller",
        params={
            "count": count,
            "power": power,
            "toughness": toughness,
            "type": creature_type,
        },
        raw=text,
    )


def parse_gain_life(text: str):
    m = re.search(r"you\s+gain\s+(\d+)\s+life", text)
    if m:
        return GainLifeEffect(
            selector="gain_life",
            subject="controller",
            params={"amount": int(m.group(1))},
            raw=text,
        )
    return None


def parse_counters(text: str):
    m = re.search(r"put\s+(\d+)\s+\+1/\+1\s+counters?\s+on\s+(.+)", text)
    if not m:
        return None

    count = int(m.group(1))
    target = parse_target(m.group(2))

    return PutCountersEffect(
        selector="put_counters",
        subject="target",
        params={"amount": count, "target": target},
        raw=text,
    )


def parse_destroy(text: str):
    m = re.search(r"destroy\s+target\s+(.+)", text)
    if m:
        target = parse_target(m.group(1))
        return DestroyEffect(
            selector="destroy",
            subject="target",
            params={"target": target},
            raw=text,
        )
    return None


def parse_exile(text: str):
    m = re.search(r"exile\s+target\s+(.+)", text)
    if m:
        target = parse_target(m.group(1))
        return ExileEffect(
            selector="exile",
            subject="target",
            params={"target": target},
            raw=text,
        )
    return None


def parse_bounce(text: str):
    m = re.search(r"return\s+target\s+(.+)\s+to\s+its\s+owner'?s\s+hand", text)
    if m:
        target = parse_target(m.group(1))
        return BounceEffect(
            selector="bounce",
            subject="target",
            params={"target": target},
            raw=text,
        )
    return None


def parse_scry(text: str):
    m = re.search(r"scry\s+(\d+)", text)
    if m:
        return ScryEffect(
            selector="scry",
            subject="controller",
            params={"amount": int(m.group(1))},
            raw=text,
        )
    return None


def parse_mill(text: str):
    m = re.search(r"mill\s+(\d+)", text)
    if m:
        return MillEffect(
            selector="mill",
            subject="target",
            params={"amount": int(m.group(1))},
            raw=text,
        )
    return None


def parse_fight(text: str):
    if "fight" in text:
        return FightEffect(
            selector="fight",
            subject="self",
            params={},
            raw=text,
        )
    return None


def parse_lose_life(text: str):
    m = re.search(r"target\s+player\s+loses\s+(\d+)\s+life", text)
    if m:
        return LoseLifeEffect(
            selector="lose_life",
            subject="target",
            params={"amount": int(m.group(1))},
            raw=text,
        )
    return None


def parse_return_from_gy(text: str):
    m = re.search(r"return\s+target\s+(.+)\s+from\s+your\s+graveyard\s+to\s+(.+)", text)
    if m:
        target = parse_target(m.group(1))
        zone = m.group(2)
        return ReturnFromGYEffect(
            selector="return_from_gy",
            subject="target",
            params={"target": target, "destination": zone},
            raw=text,
        )
    return None


def parse_gain_control(text: str):
    m = re.search(r"gain\s+control\s+of\s+target\s+(.+)", text)
    if m:
        target = parse_target(m.group(1))
        return GainControlEffect(
            selector="gain_control",
            subject="target",
            params={"target": target},
            raw=text,
        )
    return None


def parse_tap(text: str):
    m = re.search(r"tap\s+target\s+(.+)", text)
    if m:
        target = parse_target(m.group(1))
        return TapEffect(
            selector="tap",
            subject="target",
            params={"target": target},
            raw=text,
        )
    return None


def parse_untap(text: str):
    m = re.search(r"untap\s+target\s+(.+)", text)
    if m:
        target = parse_target(m.group(1))
        return UntapEffect(
            selector="untap",
            subject="target",
            params={"target": target},
            raw=text,
        )
    return None

# ------------------------------------------------------------
# Main compiler
# ------------------------------------------------------------

def compile_effect(effect_text: str):
    text = effect_text.lower().strip()

    # 1. Mana
    if text.startswith("add"):
        effects = parse_mana_effect(text)
        if effects:
            return effects[0]

    # 2. Damage
    eff = parse_damage_effect(text)
    if eff:
        return eff

    # 3. Draw
    eff = parse_draw_effect(text)
    if eff:
        return eff
    print("TEXT:", text)
    # 4. Tokens
    print("DEBUG: calling parse_dynamic_token_effect on:", text)
    eff = parse_dynamic_token_effect(text)
    print("DEBUG: parse_dynamic_token_effect returned:", eff)
    if eff:
        return eff

    eff = parse_token_effect(text)
    if eff:
        return eff

    # 5. Gain life
    eff = parse_gain_life(text)
    if eff:
        return eff

    # 6. Counters
    eff = parse_counters(text)
    if eff:
        return eff

    # 7. Destroy
    eff = parse_destroy(text)
    if eff:
        return eff

    # 8. Exile
    eff = parse_exile(text)
    if eff:
        return eff

    # 9. Bounce
    eff = parse_bounce(text)
    if eff:
        return eff

    # 10. Scry
    eff = parse_scry(text)
    if eff:
        return eff

    # 11. Mill
    eff = parse_mill(text)
    if eff:
        return eff

    # 12. Fight
    eff = parse_fight(text)
    if eff:
        return eff

    # 13. Lose life
    eff = parse_lose_life(text)
    if eff:
        return eff

    # 14. Return from GY
    eff = parse_return_from_gy(text)
    if eff:
        return eff

    # 15. Gain control
    eff = parse_gain_control(text)
    if eff:
        return eff

    # 16. Tap / Untap
    eff = parse_tap(text)
    if eff:
        return eff

    eff = parse_untap(text)
    if eff:
        return eff

    eff = parse_flashback(text)
    if eff:
        return eff
        
    # Fallback
    return UnparsedEffect(raw=effect_text)

