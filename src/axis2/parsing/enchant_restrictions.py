# axis2/parsing/enchant_restrictions.py

import re
from axis2.schema import TargetingRules, TargetingRestriction


ENCHANT_PATTERN = re.compile(
    r"enchant\s+(creature|artifact|land|planeswalker|enchantment|permanent|player|battle)(?:\s+with\s+(.+))?",
    re.IGNORECASE
)


def parse_enchant_restriction(oracle_text: str) -> TargetingRules | None:
    """
    Parse enchant restriction from oracle text.
    
    Examples:
    - "Enchant creature" -> basic targeting
    - "Enchant creature with another Aura attached to it" -> restriction: has_another_aura_attached
    - "Enchant artifact" -> basic targeting
    """
    if not oracle_text:
        return None
    
    lines = [l.strip() for l in oracle_text.split("\n")]
    
    for line in lines:
        m = ENCHANT_PATTERN.search(line)
        if not m:
            continue
        
        target_type = m.group(1).lower()
        restriction_text = m.group(2) if m.group(2) else None
        
        rules = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=[target_type]
        )
        
        if restriction_text:
            restriction_text_lower = restriction_text.lower()
            
            if "another" in restriction_text_lower and "aura" in restriction_text_lower and "attached" in restriction_text_lower:
                rules.restrictions.append(
                    TargetingRestriction(
                        type="has_another_aura_attached",
                        conditions=[]
                    )
                )
            elif "another" in restriction_text_lower and "enchantment" in restriction_text_lower and "attached" in restriction_text_lower:
                rules.restrictions.append(
                    TargetingRestriction(
                        type="has_another_enchantment_attached",
                        conditions=[]
                    )
                )
        
        return rules
    
    return None

