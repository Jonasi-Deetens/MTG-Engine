from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, List, Optional

from .ability_graph import AbilityGraphRuntimeAdapter
from .conditions import evaluate_conditions
from .effects_helpers import normalize_card_type
from .mana import ManaCost
from .continuous_helpers import effect_sort_key, object_order, sort_effects_with_dependencies
from .state import GameObject, GameState, ResolveContext
from .zones import ZONE_BATTLEFIELD


def apply_cast_cost_modifiers(
    game_state: GameState,
    player_id: int,
    spell_obj: GameObject,
    base_cost: ManaCost,
    context: Optional[ResolveContext] = None,
) -> ManaCost:
    modifiers = gather_cast_cost_modifiers(game_state, player_id, spell_obj, context)
    if not modifiers:
        return base_cost
    ordered = sort_effects_with_dependencies(sorted(modifiers, key=effect_sort_key))
    adjusted = _clone_cost(base_cost)
    delta = sum(modifier.get("amount", 0) for modifier in ordered)
    adjusted.generic = max(0, adjusted.generic + int(delta))
    return adjusted


def gather_cast_cost_modifiers(
    game_state: GameState,
    player_id: int,
    spell_obj: GameObject,
    context: Optional[ResolveContext] = None,
) -> List[Dict[str, Any]]:
    adapter = AbilityGraphRuntimeAdapter(game_state)
    modifiers: List[Dict[str, Any]] = []
    
    for source in game_state.objects.values():
        if source.zone != ZONE_BATTLEFIELD or source.phased_out:
            continue
        
        # Check static ability graphs
        if source.ability_graphs:
            for graph in source.ability_graphs:
                if graph.get("abilityType") != "static":
                    continue
                runtime = adapter.build_runtime(graph)
                if runtime.trigger or runtime.costs:
                    continue
                effect_context = ResolveContext(
                    source_id=source.id,
                    controller_id=source.controller_id,
                    targets={"target": spell_obj.id},
                )
                if context and context.targets:
                    effect_context.targets.update(context.targets)
                if not evaluate_conditions(game_state, runtime.conditions, effect_context):
                    continue
                for effect_node in runtime.effects:
                    if not isinstance(effect_node, dict):
                        continue
                    payload = effect_node.get("effect") if "effect" in effect_node else effect_node
                    if not isinstance(payload, dict):
                        continue
                    if payload.get("type") != "modify_cast_cost":
                        continue
                    applies_to = effect_node.get("appliesTo") or payload.get("appliesTo") or "spells_you_cast"
                    if not _applies_to_player(applies_to, source.controller_id, player_id):
                        continue
                    if not _matches_card_type(payload, spell_obj):
                        continue
                    amount = int(payload.get("amount", 0))
                    if not amount:
                        amount = int(payload.get("increase", 0)) - int(payload.get("reduction", 0))
                    if amount:
                        modifiers.append({
                            "amount": amount,
                            "source_id": source.id,
                            "timestamp": source.entered_turn or game_state.turn.turn_number,
                            "timestamp_order": object_order(source),
                        })
        
        # Check temporary effects from triggered/activated abilities
        for temp_effect in source.temporary_effects:
            if temp_effect.get("type") != "modify_cast_cost":
                continue
            # Check if the effect applies to this player
            effect_controller = temp_effect.get("controller_id", source.controller_id)
            if effect_controller != player_id:
                continue
            # Check if the effect applies to this card type
            affected_types = temp_effect.get("affected_types", [])
            if affected_types:
                # affected_types are stored lowercase, so normalize spell types to lowercase for comparison
                spell_types = [t.lower() for t in (spell_obj.types or []) if isinstance(t, str)]
                if not any(t in affected_types for t in spell_types):
                    continue
            amount = int(temp_effect.get("amount", 0))
            if amount:
                modifiers.append({
                    "amount": amount,
                    "source_id": source.id,
                    "timestamp": temp_effect.get("timestamp", game_state.turn.turn_number),
                    "timestamp_order": temp_effect.get("timestamp_order", object_order(source)),
                })
    
    return modifiers


def _applies_to_player(applies_to: str, source_controller: int, player_id: int) -> bool:
    if applies_to == "spells_you_cast":
        return source_controller == player_id
    if applies_to == "spells_opponents_cast":
        return source_controller != player_id
    if applies_to == "all_spells":
        return True
    return False


def _matches_card_type(payload: Dict[str, Any], spell_obj: GameObject) -> bool:
    card_type = payload.get("cardType")
    card_types = payload.get("cardTypes") or payload.get("types")
    if card_type:
        card_types = [card_type]
    if not card_types:
        return True
    normalized = {normalize_card_type(t) for t in card_types if isinstance(t, str)}
    return any(normalize_card_type(t) in normalized for t in (spell_obj.types or []))


def _clone_cost(cost: ManaCost) -> ManaCost:
    return replace(
        cost,
        colored=dict(cost.colored),
        hybrids=list(cost.hybrids),
        two_brids=list(cost.two_brids),
        phyrexian=list(cost.phyrexian),
    )

