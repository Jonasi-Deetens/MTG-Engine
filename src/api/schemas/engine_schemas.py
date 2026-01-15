from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from api.schemas.ability_schemas import AbilityGraph


class GameObjectSnapshot(BaseModel):
    id: str
    name: str
    owner_id: int
    controller_id: int
    types: List[str]
    zone: str
    mana_value: Optional[int] = None
    power: Optional[int] = None
    toughness: Optional[int] = None
    tapped: bool = False
    damage: int = 0
    counters: Dict[str, int] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)
    protections: List[str] = Field(default_factory=list)
    attached_to: Optional[str] = None
    is_token: bool = False
    was_cast: bool = False
    is_attacking: bool = False
    is_blocking: bool = False
    phased_out: bool = False
    transformed: bool = False
    regenerate_shield: bool = False


class PlayerStateSnapshot(BaseModel):
    id: int
    life: int = 40
    mana_pool: Dict[str, int] = Field(default_factory=dict)
    library: List[str] = Field(default_factory=list)
    hand: List[str] = Field(default_factory=list)
    graveyard: List[str] = Field(default_factory=list)
    exile: List[str] = Field(default_factory=list)
    command: List[str] = Field(default_factory=list)
    battlefield: List[str] = Field(default_factory=list)
    commander_id: Optional[str] = None
    commander_tax: int = 0
    commander_damage_taken: Dict[str, int] = Field(default_factory=dict)


class TurnStateSnapshot(BaseModel):
    turn_number: int = 1
    active_player_index: int = 0
    phase: str = "beginning"
    step: str = "untap"


class StackItemSnapshot(BaseModel):
    kind: Literal["spell", "activated_ability", "triggered_ability", "ability_graph"]
    payload: Dict[str, Any] = {}
    controller_id: Optional[int] = None


class GameStateSnapshot(BaseModel):
    players: List[PlayerStateSnapshot]
    objects: List[GameObjectSnapshot]
    stack: List[StackItemSnapshot] = Field(default_factory=list)
    turn: TurnStateSnapshot = TurnStateSnapshot()
    debug_log: List[str] = Field(default_factory=list)


class ResolveContextSnapshot(BaseModel):
    source_id: Optional[str] = None
    controller_id: Optional[int] = None
    triggering_source_id: Optional[str] = None
    triggering_aura_id: Optional[str] = None
    triggering_spell_id: Optional[str] = None
    targets: Dict[str, Any] = Field(default_factory=dict)
    choices: Dict[str, Any] = Field(default_factory=dict)
    previous_results: List[Dict[str, Any]] = Field(default_factory=list)


class EngineActionRequest(BaseModel):
    action: Literal["resolve_graph", "advance_turn", "pass_priority"]
    game_state: GameStateSnapshot
    ability_graph: Optional[AbilityGraph] = None
    context: Optional[ResolveContextSnapshot] = None
    player_id: Optional[int] = None


class EngineActionResponse(BaseModel):
    game_state: GameStateSnapshot
    result: Dict[str, Any]
    debug_log: List[str] = Field(default_factory=list)
