from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .conditions import evaluate_conditions
from .effects import EffectResolver
from .state import GameState, ResolveContext


@dataclass
class RuntimeAbility:
    ability_type: str
    trigger: Optional[str]
    cost: Optional[str]
    keyword: Optional[str]
    conditions: List[Dict[str, Any]]
    effects: List[Dict[str, Any]]


class AbilityGraphRuntimeAdapter:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.effect_resolver = EffectResolver(game_state)

    def build_runtime(self, graph: Dict[str, Any]) -> RuntimeAbility:
        nodes = {node["id"]: node for node in graph.get("nodes", [])}
        edges = graph.get("edges", [])

        root_id = graph.get("rootNodeId")
        root_node = nodes.get(root_id)
        if not root_node:
            root_node = next(
                (node for node in nodes.values() if node.get("type") in ("TRIGGER", "ACTIVATED", "KEYWORD")),
                None,
            )

        trigger = None
        cost = None
        keyword = None
        if root_node:
            if root_node["type"] == "TRIGGER":
                trigger = root_node["data"].get("event")
            elif root_node["type"] == "ACTIVATED":
                cost = root_node["data"].get("cost")
            elif root_node["type"] == "KEYWORD":
                keyword = root_node["data"].get("keyword")

        adjacency: Dict[str, List[str]] = {node_id: [] for node_id in nodes.keys()}
        for edge in edges:
            adjacency.setdefault(edge["from_"], []).append(edge["to"])

        conditions: List[Dict[str, Any]] = []
        effects: List[Dict[str, Any]] = []
        visited: set[str] = set()

        def traverse(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            node = nodes.get(node_id)
            if not node:
                return
            if node["type"] == "CONDITION":
                conditions.append(node["data"])
            if node["type"] == "EFFECT":
                effects.append(node["data"])
            for next_id in adjacency.get(node_id, []):
                traverse(next_id)

        if root_node:
            for next_id in adjacency.get(root_node["id"], []):
                traverse(next_id)

        return RuntimeAbility(
            ability_type=graph.get("abilityType", "triggered"),
            trigger=trigger,
            cost=cost,
            keyword=keyword,
            conditions=conditions,
            effects=effects,
        )

    def resolve(self, graph: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        runtime_ability = self.build_runtime(graph)
        if not evaluate_conditions(self.game_state, runtime_ability.conditions, context):
            return {"status": "condition_failed", "effects": []}

        results: List[Dict[str, Any]] = []
        context.previous_results = []
        for effect in runtime_ability.effects:
            result = self.effect_resolver.apply(effect, context)
            context.previous_results.append(result)
            results.append(result)

        return {
            "status": "resolved",
            "ability_type": runtime_ability.ability_type,
            "effects": results,
        }
