from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .mana import serialize_mana_cost_symbols



_OPTIONAL_KEYWORDS = {
    "kicker": {"repeatable": False},
    "multikicker": {"repeatable": True},
    "buyback": {"repeatable": False},
    "entwine": {"repeatable": False},
    "replicate": {"repeatable": True},
    "conspire": {"repeatable": False},
}


def extract_optional_costs_from_graph(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for data in _iter_keyword_data(graph):
        key = _normalize_keyword(data.get("keyword"))
        if key not in _OPTIONAL_KEYWORDS:
            continue
        costs = _costs_from_keyword_data(data)
        cost_tag = _build_cost_tag(costs)
        entry = {
            "tag": f"{key}:{cost_tag}" if cost_tag else key,
            "kind": key,
            "costs": costs,
            "repeatable": _OPTIONAL_KEYWORDS[key]["repeatable"],
        }
        results.append(entry)
    return results


def extract_splice_costs_from_graph(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    for data in _iter_keyword_data(graph):
        if _normalize_keyword(data.get("keyword")) == "splice":
            return _costs_from_keyword_data(data)
    return []


def extract_additional_costs_from_graph(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    costs: List[Dict[str, Any]] = []
    for data in _iter_keyword_data(graph):
        key = _normalize_keyword(data.get("keyword"))
        if key not in ("additional cost", "additional_cost", "additional"):
            continue
        costs.extend(_costs_from_keyword_data(data))
    return costs


def extract_alternative_costs_from_graph(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for data in _iter_keyword_data(graph):
        key = _normalize_keyword(data.get("keyword"))
        if key in ("flashback", "overload", "escape"):
            costs = _costs_from_keyword_data(data)
            cost_text = _get_cost_text(data) or _first_mana_cost_tag(costs)
            cost_value = _get_cost_text(data) or _first_mana_cost_value(costs)
            tag = f"{key}:{cost_text}" if cost_text else key
            results.append({
                "tag": tag,
                "type": "mana",
                "cost": cost_value or cost_text,
                "keyword": key,
                "extra_costs": _alternative_extra_costs_from_keyword_data(data, key),
            })
        elif key in ("alternative cost", "alternative_cost", "alternate cost", "alternate_cost", "alternate"):
            costs = _costs_from_keyword_data(data)
            cost_text = _get_cost_text(data) or _first_mana_cost_tag(costs)
            cost_value = _get_cost_text(data) or _first_mana_cost_value(costs)
            if cost_text:
                results.append({
                    "tag": cost_text,
                    "type": "mana",
                    "cost": cost_value or cost_text,
                    "keyword": "alternate",
                    "extra_costs": _alternative_extra_costs_from_keyword_data(data, "alternate"),
                })
        elif key in ("jump-start", "jumpstart"):
            results.append({
                "tag": "jump-start",
                "type": "normal",
                "keyword": "jump-start",
                "extra_costs": _alternative_extra_costs_from_keyword_data(data, "jump-start"),
            })
        elif key in ("free", "free-cast", "free_cast"):
            results.append({
                "tag": "free",
                "type": "free",
                "keyword": "free",
                "extra_costs": _alternative_extra_costs_from_keyword_data(data, "free"),
            })
    return results


def extract_ward_costs_from_graphs(graphs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    costs: List[Dict[str, Any]] = []
    for graph in graphs:
        for data in _iter_keyword_data(graph):
            if _normalize_keyword(data.get("keyword")) != "ward":
                continue
            costs.extend(_costs_from_keyword_data(data))
    return costs


def resolve_alternative_cost_from_graph(
    graph: Optional[Dict[str, Any]],
    context: Optional[Any],
) -> tuple[Optional[str], bool, Optional[str], List[Dict[str, Any]]]:
    if not graph or not context or not isinstance(context.choices, dict):
        return None, False, None, []
    tag = context.choices.get("alternative_cost_tag")
    alt_cost = context.choices.get("alternative_cost")
    if tag:
        for entry in extract_alternative_costs_from_graph(graph):
            if entry.get("tag") != tag:
                continue
            if entry.get("type") == "free":
                return "", True, tag, entry.get("extra_costs", [])
            if entry.get("type") == "normal":
                return None, False, tag, entry.get("extra_costs", [])
            return entry.get("cost"), False, tag, entry.get("extra_costs", [])
    if alt_cost:
        return alt_cost, False, None, []
    return None, False, None, []


def _iter_keyword_data(graph: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    nodes = graph.get("nodes") or []
    for node in nodes:
        if node.get("type") != "KEYWORD":
            continue
        data = node.get("data") or {}
        if isinstance(data, dict):
            yield data


def _normalize_keyword(keyword: Optional[str]) -> str:
    if not isinstance(keyword, str):
        return ""
    return keyword.strip().lower()


def _get_cost_text(data: Dict[str, Any]) -> str:
    return data.get("cost") if isinstance(data.get("cost"), str) else ""


def _costs_from_keyword_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    costs: List[Dict[str, Any]] = []
    raw_costs = data.get("costs")
    if isinstance(raw_costs, list):
        for entry in raw_costs:
            if isinstance(entry, dict) and entry.get("type"):
                costs.append(entry)
    if not costs:
        cost_text = _get_cost_text(data)
        if cost_text and "{" in cost_text:
            costs.append({"type": "mana", "cost": cost_text})
    life_cost = data.get("lifeCost")
    if isinstance(life_cost, int) and life_cost > 0:
        costs.append({"type": "life", "amount": life_cost})
    if data.get("sacrificeCost"):
        costs.append({"type": "sacrifice"})
    return costs


def _alternative_extra_costs_from_keyword_data(data: Dict[str, Any], keyword: str) -> List[Dict[str, Any]]:
    if keyword in ("jump-start", "jumpstart"):
        return [{"type": "discard", "amount": int(data.get("number", 1) or 1)}]
    if keyword == "escape":
        amount = data.get("number")
        if isinstance(amount, int) and amount > 0:
            return [{"type": "exile_graveyard", "amount": amount, "other": True}]
    extra = data.get("extraCosts") or data.get("extra_costs") or data.get("extraCost")
    if isinstance(extra, list):
        costs: List[Dict[str, Any]] = []
        for entry in extra:
            if isinstance(entry, dict) and entry.get("type"):
                costs.append(entry)
        return costs
    return []


def _build_cost_tag(costs: List[Dict[str, Any]]) -> str:
    if not costs:
        return ""
    parts: List[str] = []
    for cost in costs:
        cost_type = cost.get("type")
        if cost_type == "mana":
            raw_cost = cost.get("cost")
            if isinstance(raw_cost, dict):
                parts.append(serialize_mana_cost_symbols(raw_cost))
            else:
                parts.append(str(raw_cost or ""))
        elif cost_type in ("life", "discard", "exile_graveyard"):
            parts.append(f"{cost_type}:{cost.get('amount', 0)}")
        elif cost_type == "tap_self":
            parts.append("tap_self")
        elif cost_type == "sacrifice_self":
            parts.append("sacrifice_self")
        elif cost_type == "tap":
            parts.append(f"tap:{cost.get('card_type') or cost.get('cardType') or 'permanent'}")
        elif cost_type == "sacrifice":
            parts.append(f"sacrifice:{cost.get('card_type') or cost.get('cardType') or 'permanent'}")
        else:
            parts.append(str(cost_type))
    return "+".join(parts)


def _first_mana_cost_value(costs: List[Dict[str, Any]]) -> Optional[Any]:
    for cost in costs:
        if cost.get("type") == "mana":
            return cost.get("cost")
    return None


def _first_mana_cost_tag(costs: List[Dict[str, Any]]) -> Optional[str]:
    value = _first_mana_cost_value(costs)
    if isinstance(value, dict):
        return serialize_mana_cost_symbols(value)
    if isinstance(value, str):
        return value
    return None

