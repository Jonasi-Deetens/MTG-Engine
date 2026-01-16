# src/api/routes/abilities.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime

# No deprecated folder references - keywords are loaded from database

from api.schemas.ability_schemas import (
    AbilityGraph,
    AbilityNode,
    AbilityEdge,
    ValidationResponse,
    ValidationError,
    NormalizedAbility,
    CardAbilityGraphResponse,
    CardAbilityGraphBulkRequest,
    CardAbilityGraphBulkResponse,
)
from api.routes.auth import get_current_user
from db.models import User, CardAbilityGraph
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

    def _get_effect_payload(node: AbilityNode) -> Dict[str, Any]:
        if node.type == "ACTIVATED" and isinstance(node.data.get("effect"), dict):
            return node.data.get("effect")
        return node.data

    def _get_effect_type(node: AbilityNode) -> str:
        payload = _get_effect_payload(node)
        if isinstance(payload, dict):
            return payload.get("type") or ""
        return ""

    max_targets_allowed = {
        "damage",
        "counters",
        "tap",
        "untap",
        "destroy",
        "exile",
        "return",
        "sacrifice",
        "attach",
        "put_onto_battlefield",
        "protection",
        "gain_keyword",
        "change_power_toughness",
        "fight",
        "mill",
        "discard",
        "reveal",
        "copy_spell",
        "copy_permanent",
        "enter_copy",
        "redirect_damage",
        "counter_spell",
        "regenerate",
        "phase_out",
        "transform",
        "flicker",
        "change_control",
        "prevent_damage",
    }
    
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
    effect_nodes = [
        n for n in graph.nodes
        if n.type == "EFFECT" or (n.type == "ACTIVATED" and isinstance(n.data.get("effect"), dict))
    ]
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
    
    # Check for invalid maxTargets values
    for node in effect_nodes:
        payload = _get_effect_payload(node)
        max_targets = payload.get("maxTargets")
        if max_targets is None:
            continue
        try:
            max_targets_int = int(max_targets)
        except (TypeError, ValueError):
            errors.append(ValidationError(
                type="error",
                message=f"Effect {node.id} has invalid maxTargets value",
                nodeId=node.id
            ))
            continue
        if max_targets_int < 1:
            errors.append(ValidationError(
                type="error",
                message=f"Effect {node.id} must have maxTargets >= 1",
                nodeId=node.id
            ))
        effect_type = _get_effect_type(node)
        if effect_type and effect_type not in max_targets_allowed:
            errors.append(ValidationError(
                type="error",
                message=f"Effect {node.id} does not support maxTargets",
                nodeId=node.id
            ))
        if max_targets_int > 10:
            warnings.append(ValidationError(
                type="warning",
                message=f"Effect {node.id} has a large maxTargets value",
                nodeId=node.id
            ))

    # Validate type/color inputs for new layer effects
    valid_colors = {"W", "U", "B", "R", "G"}
    valid_types = {
        "Creature", "Artifact", "Enchantment", "Land", "Planeswalker",
        "Instant", "Sorcery", "Battle", "Tribal", "Legendary",
    }
    for node in effect_nodes:
        payload = _get_effect_payload(node)
        effect_type = _get_effect_type(node)
        if node.type == "EFFECT":
            ability_type = node.data.get("abilityType")
            if ability_type in ("static", "continuous"):
                if effect_type and effect_type not in {
                    "set_types",
                    "add_type",
                    "remove_type",
                    "set_colors",
                    "add_color",
                    "remove_color",
                    "gain_keyword",
                    "change_power_toughness",
                    "change_control",
                    "cda_power_toughness",
                }:
                    errors.append(ValidationError(
                        type="error",
                        message=f"Effect {node.id} is not allowed for {ability_type} abilities",
                        nodeId=node.id
                    ))
        if effect_type in ("set_types", "add_type", "remove_type"):
            types = payload.get("types") if effect_type == "set_types" else [payload.get("typeName")]
            if not types or not all(isinstance(t, str) for t in types):
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} must specify valid types",
                    nodeId=node.id
                ))
                continue
            invalid = [t for t in types if t not in valid_types]
            if invalid:
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} has invalid types: {', '.join(invalid)}",
                    nodeId=node.id
                ))
        if effect_type in ("set_colors", "add_color", "remove_color"):
            colors = payload.get("colors") if effect_type == "set_colors" else [payload.get("color")]
            if not colors or not all(isinstance(c, str) for c in colors):
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} must specify valid colors",
                    nodeId=node.id
                ))
                continue
            invalid = [c for c in colors if c not in valid_colors]
            if invalid:
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} has invalid colors: {', '.join(invalid)}",
                    nodeId=node.id
                ))
        if effect_type == "cda_power_toughness":
            source = payload.get("cdaSource")
            cda_set = payload.get("cdaSet", "both")
            if source not in ("controlled", "zone"):
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} must define cdaSource",
                    nodeId=node.id
                ))
            if source == "controlled":
                cda_type = payload.get("cdaType")
                if not isinstance(cda_type, str):
                    errors.append(ValidationError(
                        type="error",
                        message=f"Effect {node.id} must define cdaType",
                        nodeId=node.id
                    ))
            if source == "zone":
                cda_zone = payload.get("cdaZone")
                if cda_zone not in ("hand", "graveyard", "all_graveyards"):
                    errors.append(ValidationError(
                        type="error",
                        message=f"Effect {node.id} must define cdaZone",
                        nodeId=node.id
                    ))
            if cda_set not in ("both", "power", "toughness"):
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} has invalid cdaSet value",
                    nodeId=node.id
                ))
        if effect_type == "replace_zone_change":
            replacement_zone = payload.get("replacementZone")
            if not isinstance(replacement_zone, str):
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} must define replacementZone",
                    nodeId=node.id
                ))
            from_zone = payload.get("fromZone")
            to_zone = payload.get("toZone")
            if from_zone is not None and not isinstance(from_zone, str):
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} has invalid fromZone",
                    nodeId=node.id
                ))
            if to_zone is not None and not isinstance(to_zone, str):
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} has invalid toZone",
                    nodeId=node.id
                ))
        if effect_type == "enter_choice":
            choice_type = payload.get("choice")
            if choice_type not in ("color", "creature_type", "card_type", "target"):
                errors.append(ValidationError(
                    type="error",
                    message=f"Effect {node.id} must define a valid choice type",
                    nodeId=node.id
                ))
            choice_value = payload.get("choiceValue")
            if choice_type == "color" and choice_value:
                if choice_value not in valid_colors:
                    errors.append(ValidationError(
                        type="error",
                        message=f"Effect {node.id} has invalid choice color: {choice_value}",
                        nodeId=node.id
                    ))
            if choice_type == "card_type" and isinstance(choice_value, str) and choice_value:
                normalized = choice_value[:1].upper() + choice_value[1:].lower()
                if normalized not in valid_types:
                    errors.append(ValidationError(
                        type="error",
                        message=f"Effect {node.id} has invalid choice card type: {choice_value}",
                        nodeId=node.id
                    ))

    # Check color-pie restrictions
    if card_colors:
        for node in effect_nodes:
            effect_type = _get_effect_type(node)
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


@router.post("/cards/{card_id}/graph", response_model=CardAbilityGraphResponse)
def save_card_ability_graph(
    card_id: str,
    ability_graph: AbilityGraph,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Save or update an ability graph for a specific card."""
    print(f"[DEBUG] Saving graph for card_id: '{card_id}' (type: {type(card_id)}, len: {len(card_id) if card_id else 0}), user_id: {user.id}")
    
    # Validate card_id - check for None, empty string, or the literal string "undefined"
    # Convert to string and strip whitespace
    if card_id is None:
        print(f"[DEBUG] card_id is None")
        raise HTTPException(status_code=400, detail="Invalid card_id provided: card_id is None")
    
    card_id_str = str(card_id).strip()
    if card_id_str == "":
        print(f"[DEBUG] card_id is empty string after strip")
        raise HTTPException(status_code=400, detail="Invalid card_id provided: card_id is empty")
    
    if card_id_str.lower() == "undefined" or card_id_str.lower() == "null":
        print(f"[DEBUG] card_id is the string '{card_id_str}'")
        raise HTTPException(status_code=400, detail=f"Invalid card_id provided: '{card_id_str}'")
    
    # Use the cleaned card_id
    card_id = card_id_str
    
    try:
        # Get the card to find its name
        from db.models import Axis1CardModel
        card = db.query(Axis1CardModel).filter(Axis1CardModel.card_id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Use the name field from the model to find all versions
        card_name = card.name
        if not card_name:
            raise HTTPException(status_code=404, detail="Card name not found")
        
        # Find all cards with the same name
        all_versions = db.query(Axis1CardModel).filter(
            Axis1CardModel.name == card_name
        ).all()
        
        print(f"[DEBUG] Found {len(all_versions)} versions of card '{card_name}'")
        
        saved_graphs = []
        for version in all_versions:
            # Check if graph exists for this version
            existing = db.query(CardAbilityGraph).filter(
                CardAbilityGraph.card_id == version.card_id,
                CardAbilityGraph.user_id == user.id
            ).first()
            
            if existing:
                # Update existing graph
                existing.ability_graph_json = ability_graph.model_dump()
                existing.updated_at = datetime.utcnow()
                saved_graphs.append(existing)
            else:
                # Create new graph
                new_graph = CardAbilityGraph(
                    card_id=version.card_id,
                    user_id=user.id,
                    ability_graph_json=ability_graph.model_dump()
                )
                db.add(new_graph)
                saved_graphs.append(new_graph)
        
        db.commit()
        
        # Refresh all saved graphs
        for graph in saved_graphs:
            db.refresh(graph)
        
        # Return the graph for the requested card_id
        result = next((g for g in saved_graphs if g.card_id == card_id), saved_graphs[0])
        
        print(f"[DEBUG] Saved graph to {len(saved_graphs)} versions, returning graph for card_id: {result.card_id}")
        
        return CardAbilityGraphResponse(
            id=result.id,
            card_id=result.card_id,
            ability_graph=AbilityGraph(**result.ability_graph_json),
            created_at=result.created_at.isoformat(),
            updated_at=result.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to save ability graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save ability graph: {str(e)}")


def _find_card_ability_graph(
    db: Session,
    user: User,
    card_id: str,
) -> Optional[CardAbilityGraphResponse]:
    print(f"[DEBUG] Loading graph for card_id: {card_id}, user_id: {user.id}")

    graph = db.query(CardAbilityGraph).filter(
        CardAbilityGraph.card_id == card_id,
        CardAbilityGraph.user_id == user.id
    ).first()

    if graph:
        print(f"[DEBUG] Found graph for card_id: {graph.card_id}, id: {graph.id}")
        return CardAbilityGraphResponse(
            id=graph.id,
            card_id=graph.card_id,
            ability_graph=AbilityGraph(**graph.ability_graph_json),
            created_at=graph.created_at.isoformat(),
            updated_at=graph.updated_at.isoformat()
        )

    print(f"[DEBUG] No graph found for card_id: {card_id}, checking other versions...")
    from db.models import Axis1CardModel
    card = db.query(Axis1CardModel).filter(Axis1CardModel.card_id == card_id).first()
    if not card or not card.name:
        return None

    all_versions = db.query(Axis1CardModel).filter(
        Axis1CardModel.name == card.name
    ).all()

    print(f"[DEBUG] Checking {len(all_versions)} versions for saved graph...")
    for version in all_versions:
        graph = db.query(CardAbilityGraph).filter(
            CardAbilityGraph.card_id == version.card_id,
            CardAbilityGraph.user_id == user.id
        ).first()
        if graph:
            print(f"[DEBUG] Found graph for version card_id: {graph.card_id}, returning with requested card_id: {card_id}")
            return CardAbilityGraphResponse(
                id=graph.id,
                card_id=card_id,
                ability_graph=AbilityGraph(**graph.ability_graph_json),
                created_at=graph.created_at.isoformat(),
                updated_at=graph.updated_at.isoformat()
            )

    print(f"[DEBUG] No graph found for any version of card '{card.name}'")
    return None


@router.get("/cards/{card_id}/graph", response_model=CardAbilityGraphResponse)
def get_card_ability_graph(
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get the ability graph for a specific card, checking all versions if not found."""
    response = _find_card_ability_graph(db, user, card_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Ability graph not found for this card or any of its versions")
    return response


@router.post("/cards/graphs", response_model=CardAbilityGraphBulkResponse)
def get_card_ability_graphs(
    payload: CardAbilityGraphBulkRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get ability graphs for multiple card IDs."""
    graphs: List[CardAbilityGraphResponse] = []
    missing: List[str] = []
    for card_id in payload.card_ids:
        response = _find_card_ability_graph(db, user, card_id)
        if response is None:
            missing.append(card_id)
        else:
            graphs.append(response)
    return CardAbilityGraphBulkResponse(graphs=graphs, missing=missing)


@router.delete("/cards/{card_id}/graph")
def delete_card_ability_graph(
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete the ability graph for a specific card."""
    graph = db.query(CardAbilityGraph).filter(
        CardAbilityGraph.card_id == card_id,
        CardAbilityGraph.user_id == user.id
    ).first()
    
    if not graph:
        raise HTTPException(status_code=404, detail="Ability graph not found for this card")
    
    try:
        db.delete(graph)
        db.commit()
        return {"message": "Ability graph deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete ability graph: {str(e)}")

