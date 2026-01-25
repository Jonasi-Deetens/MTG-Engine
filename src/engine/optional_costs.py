from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def extract_optional_costs_from_graph(graph: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not graph:
        return []
    costs = graph.get("optionalCosts") if isinstance(graph, dict) else None
    if isinstance(costs, list):
        return [entry for entry in costs if isinstance(entry, dict)]
    return []


def extract_splice_costs_from_graph(graph: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not graph:
        return []
    # Splice costs are not modeled in unified effect graphs yet.
    return []


def extract_additional_costs_from_graph(graph: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not graph:
        return []
    costs = graph.get("additionalCosts") if isinstance(graph, dict) else None
    if isinstance(costs, list):
        return [entry for entry in costs if isinstance(entry, dict)]
    return []


def extract_alternative_costs_from_graph(graph: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not graph:
        return []
    # Alternative casting costs are not modeled in unified effect graphs yet.
    return []


def extract_ward_costs_from_graphs(graphs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Ward costs are not modeled in unified effect graphs yet.
    return []


def resolve_alternative_cost_from_graph(
    graph: Optional[Dict[str, Any]],
    context: Optional[Any],
) -> tuple[Optional[str], bool, Optional[str], List[Dict[str, Any]]]:
    if not graph or not context:
        return None, False, None, []
    # Alternative cost selection is not modeled in unified effect graphs yet.
    return None, False, None, []
