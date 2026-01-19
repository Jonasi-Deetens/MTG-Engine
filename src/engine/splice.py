from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ability_graph import AbilityGraphRuntimeAdapter
from .costs import pay_costs
from .optional_costs import extract_splice_costs_from_graph
from .state import GameObject, GameState, ResolveContext


def apply_splice_choices(
    game_state: GameState,
    player_id: int,
    ability_graph: Optional[dict],
    context: ResolveContext,
) -> None:
    if not ability_graph or not isinstance(context.choices, dict):
        return
    splice_cards = context.choices.get("splice_cards")
    if not isinstance(splice_cards, list) or not splice_cards:
        return
    spell_obj = game_state.objects.get(context.source_id) if context.source_id else None
    if not spell_obj or "Arcane" not in (spell_obj.types or []):
        raise ValueError("Splice can only be applied to Arcane spells.")

    combined_costs: List[Dict[str, Any]] = []
    splice_effects: List[Dict[str, Any]] = []
    adapter = AbilityGraphRuntimeAdapter(game_state)

    for card_id in splice_cards:
        card_obj = game_state.objects.get(card_id)
        if not card_obj:
            raise ValueError("Splice card not found.")
        player = game_state.get_player(player_id)
        if card_id not in player.hand:
            raise ValueError("Splice card must be in hand.")
        card_graph = card_obj.ability_graphs[0] if card_obj.ability_graphs else None
        if not card_graph:
            raise ValueError("Splice card has no ability graph.")
        costs = extract_splice_costs_from_graph(card_graph)
        if not costs:
            raise ValueError("Splice card is missing a splice cost.")
        combined_costs.extend(costs)
        runtime = adapter.build_runtime(card_graph)
        splice_effects.extend(runtime.effects)

    if combined_costs:
        pay_costs(
            game_state,
            player_id,
            spell_obj,
            combined_costs,
            context.choices,
            "splice_payments",
        )
    if splice_effects:
        context.choices["splice_effects"] = splice_effects
        context.choices["spliced_cards"] = splice_cards

