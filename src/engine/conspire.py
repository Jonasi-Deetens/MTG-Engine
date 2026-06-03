from __future__ import annotations

from typing import Iterable, Optional

from .state import GameObject, GameState


def apply_conspire_cost(
    game_state: GameState,
    player_id: int,
    spell_obj: GameObject,
    creature_ids: Optional[Iterable[str]],
) -> None:
    if not creature_ids:
        raise ValueError("Conspire requires two creatures to tap.")
    creature_list = list(creature_ids)
    if len(creature_list) != 2:
        raise ValueError("Conspire requires exactly two creatures to tap.")
    if not spell_obj.colors:
        raise ValueError("Conspire cannot be paid for a colorless spell.")
    spell_colors = set(spell_obj.colors)
    for creature_id in creature_list:
        creature = game_state.objects.get(creature_id)
        if not creature:
            raise ValueError("Conspire creature not found.")
        if creature.controller_id != player_id:
            raise ValueError("Conspire creature must be controlled by the caster.")
        if creature.zone != "battlefield":
            raise ValueError("Conspire creature must be on the battlefield.")
        if "Creature" not in creature.types:
            raise ValueError("Conspire requires creatures.")
        if creature.tapped:
            raise ValueError("Conspire creature is already tapped.")
        if not spell_colors.intersection(creature.colors or []):
            raise ValueError("Conspire creature must share a color with the spell.")
    for creature_id in creature_list:
        creature = game_state.objects.get(creature_id)
        if creature:
            creature.tapped = True

