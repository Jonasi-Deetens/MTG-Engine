from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

from .mana import MANA_SYMBOL_PATTERN, can_pay_cost, can_pay_cost_with_payment, parse_mana_cost, pay_cost, pay_cost_with_payment
from .state import GameObject, GameState
from .zones import ZONE_BATTLEFIELD, ZONE_EXILE, ZONE_GRAVEYARD


_TEXT_SEPARATOR = re.compile(r"[,;]")


def parse_cost_string(cost_text: Optional[str]) -> List[Dict[str, Any]]:
    if not cost_text:
        return []
    segments = [segment.strip() for segment in _TEXT_SEPARATOR.split(cost_text) if segment.strip()]
    costs: List[Dict[str, Any]] = []
    for segment in segments:
        costs.extend(_parse_cost_segment(segment))
    return costs


def parse_ward_keywords(keywords: Iterable[str]) -> List[Dict[str, Any]]:
    costs: List[Dict[str, Any]] = []
    for keyword in keywords:
        if not isinstance(keyword, str):
            continue
        if not keyword.lower().startswith("ward"):
            continue
        costs.extend(_parse_ward_keyword(keyword))
    return costs


def parse_additional_cast_costs(oracle_text: Optional[str]) -> List[Dict[str, Any]]:
    if not oracle_text:
        return []
    costs: List[Dict[str, Any]] = []
    for line in oracle_text.split("\n"):
        match = re.search(r"additional cost to cast[^,]*,\s*(.+)", line, flags=re.IGNORECASE)
        if not match:
            continue
        raw = match.group(1)
        if "." in raw:
            raw = raw.split(".", 1)[0]
        costs.extend(parse_cost_string(raw.strip()))
    return costs


def parse_alternative_cast_costs(oracle_text: Optional[str]) -> List[Dict[str, Any]]:
    if not oracle_text:
        return []
    costs: List[Dict[str, Any]] = []
    for line in oracle_text.split("\n"):
        flashback = re.search(r"flashback\s+(\{[^}]+\}(?:\{[^}]+\})*)", line, flags=re.IGNORECASE)
        if flashback:
            cost_text = flashback.group(1)
            costs.append({"tag": f"flashback:{cost_text}", "type": "mana", "cost": cost_text, "zone": "graveyard"})
        escape = re.search(r"escape\s+(\{[^}]+\}(?:\{[^}]+\})*)", line, flags=re.IGNORECASE)
        if escape:
            cost_text = escape.group(1)
            costs.append({"tag": f"escape:{cost_text}", "type": "mana", "cost": cost_text, "zone": "graveyard"})
        if re.search(r"jump-start", line, flags=re.IGNORECASE):
            costs.append({"tag": "jump-start", "type": "normal", "zone": "graveyard"})
        if re.search(r"overload", line, flags=re.IGNORECASE):
            overload = re.search(r"overload\s+(\{[^}]+\}(?:\{[^}]+\})*)", line, flags=re.IGNORECASE)
            if overload:
                cost_text = overload.group(1)
                costs.append({"tag": f"overload:{cost_text}", "type": "mana", "cost": cost_text})
        if re.search(r"without paying its mana cost", line, flags=re.IGNORECASE):
            costs.append({"tag": "free", "type": "free"})
        match = re.search(
            r"you may cast this spell for\s+(\{[^}]+\}(?:\{[^}]+\})*)",
            line,
            flags=re.IGNORECASE,
        )
        if match:
            cost_text = match.group(1)
            costs.append({"tag": cost_text, "type": "mana", "cost": cost_text})
    return costs


def parse_alternative_extra_costs(oracle_text: Optional[str], alt_tag: Optional[str]) -> List[Dict[str, Any]]:
    if not oracle_text or not alt_tag:
        return []
    if alt_tag == "jump-start":
        return [{"type": "discard", "amount": 1}]
    if alt_tag.startswith("escape"):
        for line in oracle_text.split("\n"):
            if "escape" not in line.lower():
                continue
            if "—" in line:
                tail = line.split("—", 1)[1]
            elif "-" in line:
                tail = line.split("-", 1)[1]
            else:
                tail = ""
            tail = tail.strip()
            if tail:
                return parse_cost_string(tail)
    return []


def pay_activation_costs(
    game_state: GameState,
    player_id: int,
    source_obj: GameObject,
    costs: List[Dict[str, Any]],
    choices: Optional[Dict[str, Any]],
) -> None:
    pay_costs(game_state, player_id, source_obj, costs, choices, "cost_payments")


def pay_costs(
    game_state: GameState,
    player_id: int,
    source_obj: GameObject,
    costs: List[Dict[str, Any]],
    choices: Optional[Dict[str, Any]],
    choice_key: str,
) -> None:
    if not costs:
        return
    cost_payments = choices.get(choice_key) if isinstance(choices, dict) else None
    payment_entry: Any = cost_payments
    if isinstance(cost_payments, dict):
        payment_entry = cost_payments.get(source_obj.id, cost_payments)
    for index, cost in enumerate(costs):
        entry: Dict[str, Any] = {}
        if isinstance(payment_entry, list) and index < len(payment_entry):
            entry = payment_entry[index] or {}
        elif isinstance(payment_entry, dict):
            entry = payment_entry
        cost_type = cost.get("type")
        if cost_type == "mana":
            mana_cost = parse_mana_cost(cost.get("cost"), x_value=0)
            payment = entry.get("mana_payment")
            payment_detail = entry.get("mana_payment_detail")
            if payment is not None:
                if not can_pay_cost_with_payment(
                    game_state.get_player(player_id).mana_pool,
                    mana_cost,
                    payment,
                    payment_detail,
                ):
                    raise ValueError("Not enough mana to pay activation cost.")
                pay_cost_with_payment(game_state, player_id, mana_cost, payment, payment_detail)
                continue
            if not can_pay_cost(game_state.get_player(player_id).mana_pool, mana_cost):
                raise ValueError("Not enough mana to activate ability.")
            pay_cost(game_state, player_id, mana_cost)
            continue
        if cost_type == "life":
            amount = int(cost.get("amount", 0))
            if amount <= 0:
                continue
            player = game_state.get_player(player_id)
            if player.life < amount:
                raise ValueError("Not enough life to pay activation cost.")
            player.life -= amount
            continue
        if cost_type == "discard":
            amount = int(cost.get("amount", 1))
            discard_ids = entry.get("discard_ids")
            discard_id = entry.get("discard_id")
            if discard_ids is None and discard_id:
                discard_ids = [discard_id]
            if not isinstance(discard_ids, list) or len(discard_ids) != amount:
                raise ValueError("Activation cost not paid.")
            player = game_state.get_player(player_id)
            for card_id in discard_ids:
                if card_id not in player.hand:
                    raise ValueError("Invalid card selected to discard for activation cost.")
                game_state.move_object(card_id, ZONE_GRAVEYARD)
            continue
        if cost_type == "exile_graveyard":
            amount = int(cost.get("amount", 0))
            exile_ids = entry.get("exile_ids")
            if not isinstance(exile_ids, list) or len(exile_ids) != amount:
                raise ValueError("Activation cost not paid.")
            player = game_state.get_player(player_id)
            for card_id in exile_ids:
                if card_id == source_obj.id and cost.get("other"):
                    raise ValueError("Invalid selection for exile cost.")
                if card_id not in player.graveyard:
                    raise ValueError("Invalid card selected to exile for activation cost.")
                game_state.move_object(card_id, ZONE_EXILE)
            continue
        if cost_type == "sacrifice_self":
            if source_obj.zone != ZONE_BATTLEFIELD:
                raise ValueError("Permanent is not on the battlefield.")
            game_state.sacrifice_object(source_obj.id)
            continue
        if cost_type == "sacrifice":
            sacrifice_id = entry.get("sacrifice_id")
            if not sacrifice_id:
                raise ValueError("Activation cost not paid.")
            sacrifice_obj = game_state.objects.get(sacrifice_id)
            if not sacrifice_obj or sacrifice_obj.controller_id != player_id:
                raise ValueError("Invalid permanent selected to sacrifice for activation cost.")
            if sacrifice_obj.zone != ZONE_BATTLEFIELD:
                raise ValueError("Selected permanent is not on the battlefield.")
            card_type = cost.get("card_type")
            if card_type and card_type.capitalize() not in (sacrifice_obj.types or []):
                raise ValueError("Selected permanent does not match sacrifice cost.")
            if cost.get("nonland") and "Land" in (sacrifice_obj.types or []):
                raise ValueError("Selected permanent does not match sacrifice cost.")
            game_state.sacrifice_object(sacrifice_id)
            continue
        if cost_type == "tap_self":
            if source_obj.zone != ZONE_BATTLEFIELD or source_obj.tapped:
                raise ValueError("Permanent is already tapped.")
            source_obj.tapped = True
            continue
        if cost_type == "tap":
            tap_id = entry.get("tap_id")
            if not tap_id:
                raise ValueError("Activation cost not paid.")
            tap_obj = game_state.objects.get(tap_id)
            if not tap_obj or tap_obj.controller_id != player_id:
                raise ValueError("Invalid permanent selected to tap for activation cost.")
            if tap_obj.zone != ZONE_BATTLEFIELD or tap_obj.tapped:
                raise ValueError("Selected permanent is not an untapped permanent.")
            card_type = cost.get("card_type")
            if card_type and card_type.capitalize() not in (tap_obj.types or []):
                raise ValueError("Selected permanent does not match tap cost.")
            if cost.get("nonland") and "Land" in (tap_obj.types or []):
                raise ValueError("Selected permanent does not match tap cost.")
            tap_obj.tapped = True
            continue
        raise ValueError("Activation cost not paid.")


def _parse_ward_keyword(keyword: str) -> List[Dict[str, Any]]:
    symbols = MANA_SYMBOL_PATTERN.findall(keyword)
    if symbols:
        cost = "".join(f"{{{symbol}}}" for symbol in symbols)
        return [{"type": "mana", "cost": cost}]
    text = keyword.lower().replace("—", "-")
    if "-" in text:
        text = text.split("-", 1)[1].strip()
    text = text.replace("ward", "", 1).strip()
    if not text:
        return []
    return _parse_text_cost(text, allow_self=False)


def _parse_cost_segment(segment: str) -> List[Dict[str, Any]]:
    symbols = MANA_SYMBOL_PATTERN.findall(segment)
    if symbols:
        mana_symbols: List[str] = []
        costs: List[Dict[str, Any]] = []
        for symbol in symbols:
            if symbol.upper() == "T":
                costs.append({"type": "tap_self"})
            else:
                mana_symbols.append(symbol)
        if mana_symbols:
            cost_text = "".join(f"{{{symbol}}}" for symbol in mana_symbols)
            costs.append({"type": "mana", "cost": cost_text})
        return costs
    return _parse_text_cost(segment, allow_self=True)


def _parse_text_cost(text: str, allow_self: bool) -> List[Dict[str, Any]]:
    lower = text.lower().strip()
    if not lower:
        return []
    number_map = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }
    def _parse_amount(raw: str) -> int:
        if raw.isdigit():
            return int(raw)
        return number_map.get(raw, 0)
    match = re.search(r"pay\s+(\d+)\s+life", lower)
    if match:
        return [{"type": "life", "amount": int(match.group(1))}]
    exile_match = re.search(
        r"exile\s+(\d+|one|two|three|four|five)\s+(other\s+)?cards?\s+from\s+your\s+graveyard",
        lower,
    )
    if exile_match:
        amount = _parse_amount(exile_match.group(1))
        other = bool(exile_match.group(2))
        return [{"type": "exile_graveyard", "amount": amount, "other": other}]
    match = re.search(r"discard\s+(\d+)\s+cards?", lower)
    if match:
        return [{"type": "discard", "amount": int(match.group(1))}]
    if "discard a card" in lower:
        return [{"type": "discard", "amount": 1}]
    if "sacrifice this" in lower or "sacrifice ~" in lower or "sacrifice it" in lower:
        return [{"type": "sacrifice_self"}] if allow_self else []
    match = re.search(r"sacrifice\s+(?:a|an)?\s*(nonland\s+)?([a-z]+)?", lower)
    if match:
        nonland = bool(match.group(1))
        card_type = match.group(2)
        if card_type in ("permanent", "permanents"):
            card_type = None
        return [{"type": "sacrifice", "card_type": card_type, "nonland": nonland}]
    if "tap this" in lower or "tap ~" in lower or lower == "tap":
        return [{"type": "tap_self"}] if allow_self else []
    match = re.search(r"tap\s+(?:an|a)?\s*(untapped\s+)?(nonland\s+)?([a-z]+)?", lower)
    if match:
        nonland = bool(match.group(2))
        card_type = match.group(3)
        if card_type in ("permanent", "permanents"):
            card_type = None
        return [{"type": "tap", "card_type": card_type, "nonland": nonland}]
    return []

