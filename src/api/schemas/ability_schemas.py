# src/api/schemas/ability_schemas.py

from pydantic import BaseModel
from typing import Dict, Any, List, Literal, Optional


class AbilityNode(BaseModel):
    """Represents a single node in an ability graph."""
    id: str
    type: Literal["TRIGGER", "CONDITION", "EFFECT", "TARGET", "MODIFIER", "ACTIVATED", "KEYWORD"]
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
    """Complete ability graph structure."""
    id: Optional[str] = None
    rootNodeId: str
    nodes: List[AbilityNode]
    edges: List[AbilityEdge]
    abilityType: Literal["triggered", "activated", "static", "keyword"]


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
    keyword: Optional[str] = None
    conditions: List[Dict[str, Any]] = []
    effects: List[Dict[str, Any]] = []
    abilityType: str


class CardAbilityGraphResponse(BaseModel):
    """Response with saved ability graph."""
    id: int
    card_id: str
    ability_graph: AbilityGraph
    created_at: str
    updated_at: str

