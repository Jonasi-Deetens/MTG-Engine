# axis2/parsing/activated.py

import re
from axis1.schema import Axis1Face
from axis2.schema import ActivatedAbility, ParseContext
from axis2.parsing.costs import parse_cost_string
from axis2.parsing.effects import parse_effect_text
from axis2.parsing.targeting import parse_targeting

def strip_parenthetical(text: str) -> str:
    out = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(depth - 1, 0)
        elif depth == 0:
            out.append(ch)
    return "".join(out)

ABILITY_SPLIT_RE = re.compile(r"^(.*?):\s*(.*)$")

def split_full_ability(text: str):
    """
    Splits "COST: EFFECT" into ("COST", "EFFECT").
    """
    m = ABILITY_SPLIT_RE.match(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


def parse_activated_abilities(axis1_face: Axis1Face, ctx: ParseContext) -> list[ActivatedAbility]:
    """
    Modern, clean activated-ability parser.

    Axis1Face.activated_abilities contains objects with:
        - cost (raw string)
        - effect (raw string)
        - text (fallback)
        - cost_parts (legacy)
    """

    activated = []
    activated_abilities_list = getattr(axis1_face, "activated_abilities", [])
    
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Parsing {len(activated_abilities_list)} activated abilities from Axis1")

    for a in activated_abilities_list:
        raw_cost = getattr(a, "cost", "") or ""
        raw_effect = getattr(a, "effect", "") or ""
        raw_text = getattr(a, "text", "") or ""
        raw_effect = strip_parenthetical(raw_effect)
        
        logger.debug(f"Processing activated ability: cost='{raw_cost}', effect='{raw_effect}', text='{raw_text}'")
        # ------------------------------------------------------------
        # 1. Parse costs using the new multi-part cost parser
        # ------------------------------------------------------------
        costs = []
        if raw_cost:
            costs = parse_cost_string(raw_cost)

        # ------------------------------------------------------------
        # 2. Parse effects
        # ------------------------------------------------------------
        effects = parse_effect_text(raw_effect, ctx)
        targeting = parse_targeting(raw_effect)
        
        # Also parse replacement effects from the effect text
        # (e.g., "Until end of turn, if you would put counters...")
        # These should be attached to this ability, not the global replacement effects list
        from axis2.parsing.replacement_effects import parse_replacement_effects
        from axis2.schema import ReplacementEffect
        replacement_effects = parse_replacement_effects(raw_effect)
        # Add replacement effects to the ability's effects list
        effects.extend(replacement_effects)
        
        # Debug: log effect parsing results
        if raw_effect:
            regular_effects = [e for e in effects if not isinstance(e, ReplacementEffect)]
            logger.debug(f"Effect parsing: text='{raw_effect}', parsed {len(effects)} effects ({len(regular_effects)} regular, {len(replacement_effects)} replacement)")
            if not effects:
                logger.debug(f"WARNING: Effect text '{raw_effect}' did not parse into any effects")

        # ------------------------------------------------------------
        # 3. Fallback: Axis1 failed to split cost/effect
        # ------------------------------------------------------------
        if (not costs and not effects) and raw_text:
            cost_text, effect_text = split_full_ability(raw_text)
            effect_text = strip_parenthetical(effect_text)

            if cost_text:
                costs = parse_cost_string(cost_text)

            if effect_text:
                effects = parse_effect_text(effect_text, ctx)
                targeting = parse_targeting(effect_text)

        # ------------------------------------------------------------
        # 4. Determine timing from activation_conditions
        # ------------------------------------------------------------
        timing = "instant"  # Default
        activation_conditions = getattr(a, "activation_conditions", None) or []
        for cond in activation_conditions:
            if isinstance(cond, dict) and cond.get("type") == "timing":
                if cond.get("value") == "sorcery_only":
                    timing = "sorcery"
                    break
        
        # ------------------------------------------------------------
        # 5. Build the ActivatedAbility
        # Only add if we have at least costs or effects (don't add empty abilities)
        # ------------------------------------------------------------
        if costs or effects:
            ability = ActivatedAbility(
                costs=costs,
                effects=effects,
                conditions=activation_conditions,
                targeting=targeting,
                timing=timing,
            )
            logger.debug(f"Created ActivatedAbility: costs={len(costs)}, effects={len(effects)}, timing={timing}")
            activated.append(ability)
        else:
            logger.debug(f"Skipping activated ability with no costs or effects. cost={raw_cost}, effect={raw_effect}, text={raw_text}")

    return activated
