# src/api/routes/abilities.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

# No deprecated folder references - keywords are loaded from database

from api.schemas.ability_schemas import (
    AbilityGraph,
    AbilityNode,
    AbilityEdge,
    ValidationResponse,
    ValidationError,
    NormalizedAbility
)
from api.routes.auth import get_current_user
from db.models import User
from db.connection import SessionLocal

router = APIRouter(prefix="/api/abilities", tags=["abilities"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Color-pie restrictions
COLOR_PIE_RESTRICTIONS = {
    "R": ["DEAL_DAMAGE", "HASTE", "SACRIFICE", "DESTROY_TARGET"],
    "U": ["DRAW_CARDS", "COUNTER_SPELL", "TAP_TARGET", "RETURN_TO_HAND"],
    "G": ["ADD_COUNTERS", "RAMP", "CREATE_TOKEN", "TUTOR_LAND"],
    "B": ["DESTROY_TARGET", "DISCARD", "REMOVE_COUNTERS", "SACRIFICE"],
    "W": ["EXILE", "GAIN_LIFE", "PROTECTION", "PREVENT_DAMAGE"],
}


def validate_graph(graph: AbilityGraph, card_colors: Optional[List[str]] = None) -> ValidationResponse:
    """Validate an ability graph structure."""
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    
    # Check for at least one root node (trigger, activated, or keyword)
    trigger_nodes = [n for n in graph.nodes if n.type == "TRIGGER"]
    activated_nodes = [n for n in graph.nodes if n.type == "ACTIVATED"]
    keyword_nodes = [n for n in graph.nodes if n.type == "KEYWORD"]
    
    root_nodes = trigger_nodes + activated_nodes + keyword_nodes
    
    if len(root_nodes) == 0:
        errors.append(ValidationError(
            type="error",
            message="At least one TRIGGER, ACTIVATED, or KEYWORD node is required",
            nodeId=None
        ))
    elif len(root_nodes) > 1:
        warnings.append(ValidationError(
            type="warning",
            message="Multiple root nodes found. Only one will be used as root.",
            nodeId=None
        ))
    
    # Check for at least one effect node (unless we have a keyword node, which is self-contained)
    effect_nodes = [n for n in graph.nodes if n.type == "EFFECT"]
    if len(effect_nodes) == 0 and len(keyword_nodes) == 0:
        errors.append(ValidationError(
            type="error",
            message="At least one EFFECT node is required (or a KEYWORD node)",
            nodeId=None
        ))
    
    # Check for dangling nodes (nodes with no connections)
    connected_node_ids = set()
    for edge in graph.edges:
        connected_node_ids.add(edge.from_)
        connected_node_ids.add(edge.to)
    
    for node in graph.nodes:
        if node.id not in connected_node_ids and node.id != graph.rootNodeId:
            warnings.append(ValidationError(
                type="warning",
                message=f"Node {node.id} is not connected to the graph",
                nodeId=node.id
            ))
    
    # Check for invalid connections (EFFECT -> EFFECT, EFFECT -> TRIGGER)
    for edge in graph.edges:
        from_node = next((n for n in graph.nodes if n.id == edge.from_), None)
        to_node = next((n for n in graph.nodes if n.id == edge.to), None)
        
        if from_node and to_node:
            if from_node.type == "EFFECT" and to_node.type == "EFFECT":
                errors.append(ValidationError(
                    type="error",
                    message=f"Invalid connection: EFFECT nodes cannot connect to other EFFECT nodes",
                    nodeId=edge.from_
                ))
            if from_node.type == "EFFECT" and to_node.type == "TRIGGER":
                errors.append(ValidationError(
                    type="error",
                    message=f"Invalid connection: EFFECT nodes cannot connect to TRIGGER nodes",
                    nodeId=edge.from_
                ))
    
    # Check color-pie restrictions
    if card_colors:
        for node in effect_nodes:
            effect_type = node.data.get("effect", "")
            # Check if effect is allowed for any of the card's colors
            allowed = False
            for color in card_colors:
                if effect_type in COLOR_PIE_RESTRICTIONS.get(color, []):
                    allowed = True
                    break
            
            if not allowed and effect_type:
                warnings.append(ValidationError(
                    type="warning",
                    message=f"Effect '{effect_type}' may not fit the color pie for colors {card_colors}",
                    nodeId=node.id
                ))
    
    # Check for cycles (simple check - no node should connect back to itself through a path)
    # This is a simplified check - a full cycle detection would require DFS
    for edge in graph.edges:
        if edge.from_ == edge.to:
            errors.append(ValidationError(
                type="error",
                message=f"Node {edge.from_} connects to itself (self-loop)",
                nodeId=edge.from_
            ))
    
    return ValidationResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def normalize_graph(graph: AbilityGraph) -> NormalizedAbility:
    """Convert node graph to linear engine-friendly format."""
    # Find root node (trigger, activated, or keyword)
    root_node = next((n for n in graph.nodes if n.id == graph.rootNodeId), None)
    if not root_node:
        # Fallback: find first root node
        root_node = next(
            (n for n in graph.nodes if n.type in ["TRIGGER", "ACTIVATED", "KEYWORD"]),
            None
        )
    
    trigger = None
    cost = None
    keyword = None
    
    if root_node:
        if root_node.type == "TRIGGER":
            trigger = root_node.data.get("event", None)
        elif root_node.type == "ACTIVATED":
            cost = root_node.data.get("cost", None)
        elif root_node.type == "KEYWORD":
            keyword = root_node.data.get("keyword", None)
    
    # Build adjacency list for traversal
    adjacency: Dict[str, List[str]] = {node.id: [] for node in graph.nodes}
    for edge in graph.edges:
        if edge.from_ in adjacency:
            adjacency[edge.from_].append(edge.to)
    
    # Traverse from root to collect conditions and effects
    conditions: List[Dict[str, Any]] = []
    effects: List[Dict[str, Any]] = []
    
    if root_node:
        visited = set()
        
        def traverse(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            
            node = next((n for n in graph.nodes if n.id == node_id), None)
            if not node:
                return
            
            if node.type == "CONDITION":
                conditions.append(node.data)
            elif node.type == "EFFECT":
                effects.append(node.data)
            elif node.type == "ACTIVATED":
                # Activated nodes can have effects in their data
                if "effect" in node.data:
                    effects.append(node.data)
            
            # Continue traversal
            for next_id in adjacency.get(node_id, []):
                traverse(next_id)
        
        # Start traversal from root
        for next_id in adjacency.get(root_node.id, []):
            traverse(next_id)
    
    return NormalizedAbility(
        trigger=trigger,
        cost=cost,
        keyword=keyword,
        conditions=conditions,
        effects=effects,
        abilityType=graph.abilityType
    )


@router.post("/validate", response_model=ValidationResponse)
def validate_ability_graph(
    graph: AbilityGraph,
    card_colors: Optional[List[str]] = None,
    user: User = Depends(get_current_user)
):
    """Validate an ability graph structure."""
    return validate_graph(graph, card_colors)


@router.post("/normalize", response_model=NormalizedAbility)
def normalize_ability_graph(
    graph: AbilityGraph,
    user: User = Depends(get_current_user)
):
    """Convert graph to engine-friendly format."""
    return normalize_graph(graph)


# Known keywords with parameters - based on parser analysis
KEYWORD_PARAMETERS = {
    # Keywords with mana costs
    "ward": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "kicker": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "multikicker": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "flashback": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "buyback": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "evoke": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "morph": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "megamorph": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "bestow": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "awaken": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "overload": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "splice": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "entwine": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "replicate": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "surge": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "escape": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "retrace": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "jump-start": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "disturb": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "embalm": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "eternalize": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "unearth": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "dash": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "ninjutsu": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "commander ninjutsu": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "foretell": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "suspend": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "transmute": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "dredge": {"has_cost": True, "has_mana_cost": False, "cost_type": "life"},
    "recover": {"has_cost": True, "has_mana_cost": False, "cost_type": "life"},
    "madness": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "blitz": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "casualty": {"has_cost": True, "has_mana_cost": False, "cost_type": "sacrifice"},
    "cleave": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "spree": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    
    # Keywords with number parameters
    "annihilator": {"has_number": True, "number_type": "annihilator"},
    "bloodthirst": {"has_number": True, "number_type": "bloodthirst"},
    "absorb": {"has_number": True, "number_type": "absorb"},
    "bushido": {"has_number": True, "number_type": "bushido"},
    "frenzy": {"has_number": True, "number_type": "frenzy"},
    "melee": {"has_number": True, "number_type": "melee"},
    "poisonous": {"has_number": True, "number_type": "poisonous"},
    "renown": {"has_number": True, "number_type": "renown"},
    "skulk": {"has_number": True, "number_type": "skulk"},
    "toxic": {"has_number": True, "number_type": "toxic"},
    "training": {"has_number": False},  # Has condition but no number
    "modular": {"has_number": True, "number_type": "modular"},
    "sunburst": {"has_number": False},  # Based on colors
    "level up": {"has_number": True, "number_type": "level"},
    "outlast": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "bolster": {"has_number": True, "number_type": "bolster"},
    "support": {"has_number": True, "number_type": "support"},
    "fabricate": {"has_number": True, "number_type": "fabricate"},
    "evolve": {"has_number": False},
    "mentor": {"has_number": False},
    "riot": {"has_number": False},  # Has choice
    "adapt": {"has_number": True, "number_type": "adapt"},
    "amass": {"has_number": True, "number_type": "amass"},
    "proliferate": {"has_number": False},
    "scavenge": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "undying": {"has_number": False},
    "persist": {"has_number": False},
    "wither": {"has_number": False},
    "infect": {"has_number": False},
    "devour": {"has_number": True, "number_type": "devour"},
    "graft": {"has_number": True, "number_type": "graft"},
    "vanishing": {"has_number": True, "number_type": "vanishing"},
    "fading": {"has_number": True, "number_type": "fading"},
    "cumulative upkeep": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "echo": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "rampage": {"has_number": True, "number_type": "rampage"},
    "flanking": {"has_number": False},
    "banding": {"has_number": False},
    "phasing": {"has_number": False},
    "afflict": {"has_number": True, "number_type": "afflict"},
    "aftermath": {"has_number": False},
    "embalm": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "eternalize": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "backup": {"has_number": True, "number_type": "backup"},
    "training": {"has_number": False},
    "read ahead": {"has_number": False},
    "squad": {"has_number": True, "number_type": "squad"},
    "bargain": {"has_cost": True, "has_mana_cost": False, "cost_type": "sacrifice"},
    "craft": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "disguise": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "plot": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "saddle": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "freerunning": {"has_number": True, "number_type": "freerunning"},
    "gift": {"has_number": True, "number_type": "gift"},
    "offspring": {"has_number": True, "number_type": "offspring"},
    "impending": {"has_number": False},
    "extort": {"has_number": False},
    "fuse": {"has_number": False},
    "tribute": {"has_number": False},
    "dethrone": {"has_number": False},
    "enlist": {"has_number": False},
    "ravenous": {"has_number": True, "number_type": "ravenous"},
    "space sculptor": {"has_number": False},
    "visit": {"has_number": False},
    "prototype": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "living metal": {"has_number": False},
    "for mirrodin!": {"has_number": False},
    "for mirrodin": {"has_number": False},
    "compleated": {"has_number": False},
    "reconfigure": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "living weapon": {"has_number": False},
    "myriad": {"has_number": False},
    "partner": {"has_number": False},
    "companion": {"has_number": False},
    "mutate": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "encore": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "emerge": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "exploit": {"has_number": False},
    "prowess": {"has_number": False},
    "ingest": {"has_number": False},
    "devoid": {"has_number": False},
    "improvise": {"has_number": False},
    "convoke": {"has_number": False},
    "affinity": {"has_number": False},  # Based on artifact count
    "delve": {"has_number": False},
    "fortify": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "equip": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "reinforce": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "cycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "basic landcycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "islandcycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "swampcycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "mountaincycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "forestcycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "plaincycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "wizardcycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
    "slivercycling": {"has_cost": True, "has_mana_cost": True, "cost_type": "mana"},
}

def _extract_keyword_options(parser, keyword_name: str) -> Dict[str, Any]:
    """Extract configurable options from a keyword parser."""
    keyword_lower = keyword_name.lower()
    
    # Check known parameters first
    if keyword_lower in KEYWORD_PARAMETERS:
        return {
            "has_cost": KEYWORD_PARAMETERS[keyword_lower].get("has_cost", False),
            "has_number": KEYWORD_PARAMETERS[keyword_lower].get("has_number", False),
            "has_mana_cost": KEYWORD_PARAMETERS[keyword_lower].get("has_mana_cost", False),
            "cost_type": KEYWORD_PARAMETERS[keyword_lower].get("cost_type"),
            "number_type": KEYWORD_PARAMETERS[keyword_lower].get("number_type"),
            "description": f"{keyword_name} keyword ability",
        }
    
    # Default for simple keywords
    return {
        "has_cost": False,
        "has_number": False,
        "has_mana_cost": False,
        "cost_type": None,
        "number_type": None,
        "description": f"{keyword_name} keyword ability",
    }


@router.get("/keywords")
def list_keywords(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all available keyword abilities from the database with their options."""
    try:
        from db.models import Keyword
        
        keywords = db.query(Keyword).order_by(Keyword.name).all()
        
        keyword_list = []
        for kw in keywords:
            options = {
                "has_cost": kw.has_cost,
                "has_number": kw.has_number,
                "has_mana_cost": kw.has_mana_cost,
                "has_life_cost": kw.has_life_cost,
                "has_sacrifice_cost": kw.has_sacrifice_cost,
                "has_discard_cost": kw.has_discard_cost,
                "cost_type": kw.cost_type,
                "number_type": kw.number_type,
                "description": kw.description,
            }
            
            keyword_list.append({
                "name": kw.name,
                "has_parser": True,  # All keywords in DB are valid
                "options": options
            })
        
        return {
            "keywords": keyword_list,
            "total": len(keyword_list)
        }
    except Exception as e:
        import traceback
        return {
            "keywords": [],
            "total": 0,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@router.get("/templates")
def get_templates(user: User = Depends(get_current_user)):
    """Get ability templates."""
    templates = [
        {
            "id": "etb_damage",
            "name": "Enter the Battlefield - Deal Damage",
            "description": "When this creature enters the battlefield, deal 2 damage to any target.",
            "graph": {
                "rootNodeId": "trigger1",
                "nodes": [
                    {
                        "id": "trigger1",
                        "type": "TRIGGER",
                        "data": {"event": "ON_ENTER_BATTLEFIELD"}
                    },
                    {
                        "id": "effect1",
                        "type": "EFFECT",
                        "data": {"effect": "DEAL_DAMAGE", "amount": 2, "target": "ANY"}
                    }
                ],
                "edges": [
                    {"from_": "trigger1", "to": "effect1"}
                ],
                "abilityType": "triggered"
            }
        },
        {
            "id": "attack_draw",
            "name": "Attack - Draw Card",
            "description": "Whenever this creature attacks, draw a card.",
            "graph": {
                "rootNodeId": "trigger1",
                "nodes": [
                    {
                        "id": "trigger1",
                        "type": "TRIGGER",
                        "data": {"event": "ON_ATTACK"}
                    },
                    {
                        "id": "effect1",
                        "type": "EFFECT",
                        "data": {"effect": "DRAW_CARDS", "amount": 1}
                    }
                ],
                "edges": [
                    {"from_": "trigger1", "to": "effect1"}
                ],
                "abilityType": "triggered"
            }
        },
        {
            "id": "death_token",
            "name": "Death - Create Token",
            "description": "When this creature dies, create a 1/1 token.",
            "graph": {
                "rootNodeId": "trigger1",
                "nodes": [
                    {
                        "id": "trigger1",
                        "type": "TRIGGER",
                        "data": {"event": "ON_DEATH"}
                    },
                    {
                        "id": "effect1",
                        "type": "EFFECT",
                        "data": {
                            "effect": "CREATE_TOKEN",
                            "power": 1,
                            "toughness": 1,
                            "token_type": "creature"
                        }
                    }
                ],
                "edges": [
                    {"from_": "trigger1", "to": "effect1"}
                ],
                "abilityType": "triggered"
            }
        }
    ]
    
    return {"templates": templates}


@router.post("/templates")
def save_template(
    template: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    """Save a custom template (placeholder - would store in database)."""
    # TODO: Implement template storage in database
    return {"message": "Template saved (not yet persisted)", "template": template}

