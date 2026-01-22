# src/api/schemas/ability_schemas.py

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Literal, Optional, Union


# =============================================================================
# New Schema Types for Refactored Ability System
# =============================================================================

class EffectCondition(BaseModel):
    """Condition that can be attached to an individual effect."""
    type: str  # 'was_cast', 'control_count', 'life_total', etc.
    target: Optional[str] = None  # 'triggering_aura', 'triggering_source', etc.
    comparison: Optional[str] = None  # '>=', '<=', '==', etc.
    value: Optional[Union[int, str]] = None
    permanentType: Optional[str] = None
    keyword: Optional[str] = None
    counterType: Optional[str] = None
    source: Optional[str] = None  # For mana_value_comparison


class TargetSpec(BaseModel):
    """Specification for effect targets with optional min/max."""
    type: Optional[str] = None  # 'creature', 'player', 'permanent', etc.
    min: Optional[int] = None  # Optional - infer from context if missing
    max: Optional[int] = None  # Optional - infer from context if missing
    scope: Optional[str] = None  # 'you_control', 'opponent_control', 'any'
    types: Optional[List[str]] = None  # Specific types like ['Creature', 'Planeswalker']


class EffectData(BaseModel):
    """Extended effect data with per-effect conditions and optional flag."""
    type: str  # 'damage', 'search', 'attach', 'draw', etc.
    optional: Optional[bool] = False  # Per-effect optional flag ("may")
    condition: Optional[EffectCondition] = None  # Per-effect condition
    fromEffect: Optional[int] = None  # Reference to previous effect result
    targets: Optional[TargetSpec] = None  # Target specification
    # Allow any additional effect-specific fields
    
    class Config:
        extra = "allow"


class TriggerData(BaseModel):
    """Trigger specification for triggered abilities."""
    event: str  # 'enters_battlefield', 'card_enters', 'upkeep', etc.
    scope: Optional[str] = "self"  # 'self', 'you_control', 'any', etc.
    cardType: Optional[str] = None  # Filter for card type
    entersWhere: Optional[str] = None  # For card_enters: 'battlefield', 'graveyard'
    entersFrom: Optional[str] = None  # For card_enters: 'library', 'hand'
    
    class Config:
        extra = "allow"


class CostData(BaseModel):
    """Cost specification for activated abilities."""
    type: str  # 'mana', 'tap_self', 'sacrifice', 'discard', etc.
    amount: Optional[Union[int, str]] = None
    manaType: Optional[str] = None  # For mana costs: 'W', 'U', 'B', 'R', 'G', 'generic'
    
    class Config:
        extra = "allow"


class Ability(BaseModel):
    """New unified ability schema with per-effect conditions and flags."""
    id: str  # e.g., "triggered-0", "activated-1"
    type: Literal["triggered", "activated", "static", "spell"]
    usesStack: bool = True  # Configurable stack behavior
    trigger: Optional[TriggerData] = None  # For triggered abilities
    costs: Optional[List[CostData]] = None  # For activated abilities
    abilityCondition: Optional[EffectCondition] = None  # Ability-level gate condition
    effects: List[EffectData] = []
    # Modal configuration
    modal: Optional[Dict[str, Any]] = None  # {min, max, modes}


class AbilityCollection(BaseModel):
    """Collection of abilities for a card, organized by type."""
    triggered: List[Ability] = []
    activated: List[Ability] = []
    static: List[Ability] = []
    spell: List[Ability] = []


# =============================================================================
# Legacy Schema Types (maintained for backward compatibility)
# =============================================================================

class AbilityNode(BaseModel):
    """Represents a single node in an ability graph."""
    id: str
    type: Literal["TRIGGER", "CONDITION", "EFFECT", "TARGET", "MODIFIER", "ACTIVATED", "KEYWORD", "SPELL"]
    data: Dict[str, Any]  # Type-specific data


class AbilityEdge(BaseModel):
    """Represents a connection between two nodes in an ability graph."""
    from_: str  # source node id (using from_ to avoid Python keyword conflict)
    to: str  # target node id
    
    class Config:
        # Allow using "from" as field name in JSON
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "from": "node1",
                "to": "node2"
            }
        }


class AbilityGraph(BaseModel):
    """Complete ability graph structure (legacy format)."""
    id: Optional[str] = None
    rootNodeId: str
    nodes: List[AbilityNode]
    edges: List[AbilityEdge]
    abilityType: Literal["triggered", "activated", "static", "keyword", "spell"]
    # New fields for refactored system
    abilityId: Optional[str] = None  # e.g., "triggered-0"
    usesStack: Optional[bool] = True  # Configurable stack behavior


class ValidationError(BaseModel):
    """Represents a validation error."""
    type: Literal["error", "warning"]
    message: str
    nodeId: Optional[str] = None


class ValidationResponse(BaseModel):
    """Response from graph validation."""
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]


class NormalizedAbility(BaseModel):
    """Engine-friendly normalized ability structure."""
    trigger: Optional[str] = None
    cost: Optional[str] = None
    costs: List[Dict[str, Any]] = []
    keyword: Optional[str] = None
    conditions: List[Dict[str, Any]] = []
    effects: List[Dict[str, Any]] = []
    abilityType: str
    # New fields for refactored system
    abilityId: Optional[str] = None  # e.g., "triggered-0"
    usesStack: Optional[bool] = True
    abilityCondition: Optional[Dict[str, Any]] = None  # Ability-level gate


class CardAbilityGraphResponse(BaseModel):
    """Response with saved ability graph."""
    id: int
    card_id: str
    ability_graph: AbilityGraph
    created_at: str
    updated_at: str
    # New fields for refactored system
    ability_type: Optional[str] = None  # 'triggered', 'activated', etc.
    ability_index: Optional[int] = None  # Index within type (0, 1, 2...)


class CardAbilityGraphBulkRequest(BaseModel):
    card_ids: List[str]


class CardAbilityGraphBulkResponse(BaseModel):
    graphs: List[CardAbilityGraphResponse]
    missing: List[str]


# =============================================================================
# New API Request/Response Types
# =============================================================================

class AbilityIdentifier(BaseModel):
    """Identifies a specific ability on a card."""
    card_id: str
    ability_type: Literal["triggered", "activated", "static", "spell"]
    ability_index: int = 0


class ActivateAbilityRequest(BaseModel):
    """Request to activate an ability."""
    player_id: int
    object_id: str
    ability_type: Literal["triggered", "activated", "static", "spell"] = "activated"
    ability_index: int = 0
    context: Optional[Dict[str, Any]] = None


class AbilityCollectionResponse(BaseModel):
    """Response with all abilities for a card organized by type."""
    card_id: str
    abilities: AbilityCollection
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
