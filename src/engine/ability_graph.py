from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .conditions import evaluate_conditions
from .choices import extract_modal_config
from .effects import EffectResolver
from .state import GameState, ResolveContext


@dataclass
class RuntimeAbility:
    ability_type: str
    trigger: Optional[str]
    trigger_data: Optional[Dict[str, Any]]
    costs: List[Dict[str, Any]]
    keyword: Optional[str]
    timing: Optional[str]
    activation_limit: Optional[Dict[str, Any]]
    conditions: List[Dict[str, Any]]
    effects: List[Dict[str, Any]]
    modal: Optional[Dict[str, Any]]


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
                (node for node in nodes.values() if node.get("type") in ("TRIGGER", "ACTIVATED", "KEYWORD", "SPELL")),
                None,
            )

        trigger = None
        trigger_data: Optional[Dict[str, Any]] = None
        costs: List[Dict[str, Any]] = []
        keyword = None
        timing = None
        activation_limit = None
        modal = extract_modal_config(graph)
        if root_node:
            if root_node["type"] == "TRIGGER":
                trigger = root_node["data"].get("event")
                trigger_data = dict(root_node.get("data") or {})
            elif root_node["type"] == "ACTIVATED":
                costs = root_node["data"].get("costs") if isinstance(root_node["data"].get("costs"), list) else []
                timing = root_node["data"].get("timing")
                activation_limit = root_node["data"].get("limit")
            elif root_node["type"] == "KEYWORD":
                keyword = root_node["data"].get("keyword")
            elif root_node["type"] == "SPELL":
                pass

        adjacency: Dict[str, List[str]] = {node_id: [] for node_id in nodes.keys()}
        for edge in edges:
            source_id = edge.get("from_") or edge.get("from")
            if not source_id:
                continue
            adjacency.setdefault(source_id, []).append(edge["to"])

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
                effect_data = dict(node["data"])
                effect_data["_node_id"] = node_id
                effects.append(effect_data)
            for next_id in adjacency.get(node_id, []):
                traverse(next_id)

        if root_node:
            if root_node["type"] == "EFFECT" and graph.get("abilityType") == "static":
                effect_data = dict(root_node.get("data", {}))
                effect_data["_node_id"] = root_node["id"]
                effects.append(effect_data)
            for next_id in adjacency.get(root_node["id"], []):
                traverse(next_id)

        return RuntimeAbility(
            ability_type=graph.get("abilityType", "triggered"),
            trigger=trigger,
            trigger_data=trigger_data,
            costs=costs,
            keyword=keyword,
            timing=timing,
            activation_limit=activation_limit,
            conditions=conditions,
            effects=effects,
            modal=modal,
        )

    def resolve(self, graph: Dict[str, Any], context: ResolveContext) -> Dict[str, Any]:
        runtime_ability = self.build_runtime(graph)
        if not evaluate_conditions(self.game_state, runtime_ability.conditions, context):
            return {"status": "condition_failed", "effects": []}

        results: List[Dict[str, Any]] = []
        context.previous_results = []
        selected_modes: Optional[List[str]] = None
        if runtime_ability.modal:
            choices = context.choices if isinstance(context.choices, dict) else {}
            raw = choices.get("chosen_modes")
            if raw is None:
                raw = choices.get("chosen_mode")
            if isinstance(raw, str):
                selected_modes = [raw]
            elif isinstance(raw, list):
                selected_modes = [entry for entry in raw if isinstance(entry, str) and entry]
            if not selected_modes:
                if choices.get("entwine") and isinstance(runtime_ability.modal.get("modes"), list):
                    selected_modes = [
                        mode.get("id")
                        for mode in runtime_ability.modal.get("modes")
                        if isinstance(mode, dict) and mode.get("id")
                    ]
                else:
                    min_required = runtime_ability.modal.get("min") if isinstance(runtime_ability.modal, dict) else None
                    min_required = int(min_required) if isinstance(min_required, int) and min_required >= 0 else 1
                    if min_required == 0:
                        selected_modes = []
                    else:
                        raise ValueError("Missing modal choices.")
        extra_effects = []
        if isinstance(context.choices, dict):
            splice_effects = context.choices.get("splice_effects")
            if isinstance(splice_effects, list):
                extra_effects = [entry for entry in splice_effects if isinstance(entry, dict)]
        for effect in runtime_ability.effects + extra_effects:
            mode_id = effect.get("modeId")
            if runtime_ability.modal and mode_id and selected_modes is not None:
                if mode_id not in selected_modes:
                    continue
            result = self.effect_resolver.apply(effect, context)
            context.previous_results.append(result)
            results.append(result)

        return {
            "status": "resolved",
            "ability_type": runtime_ability.ability_type,
            "effects": results,
        }
