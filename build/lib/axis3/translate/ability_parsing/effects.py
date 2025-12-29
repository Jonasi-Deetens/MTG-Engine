from axis3.engine.abilities.effects.mana import AddManaEffect

def parse_effect_string(effect_str: str):
    effect_str = effect_str.strip()
    is_mana_ability = False
    effects = []

    # 1. Mana abilities
    if effect_str.lower().startswith("add"):
        # Example: "Add {G}."
        if "{G}" in effect_str:
            effects.append(AddManaEffect("G"))
            is_mana_ability = True
        if "{R}" in effect_str:
            effects.append(AddManaEffect("R"))
            is_mana_ability = True
        if "{U}" in effect_str:
            effects.append(AddManaEffect("U"))
            is_mana_ability = True
        if "{B}" in effect_str:
            effects.append(AddManaEffect("B"))
            is_mana_ability = True
        if "{W}" in effect_str:
            effects.append(AddManaEffect("W"))
            is_mana_ability = True

        return effects, is_mana_ability

    # 2. Damage
    if "damage" in effect_str.lower():
        from axis3.engine.abilities.effects.damage import DealDamageEffect
        # naive parse: "Deal 1 damage to any target"
        amount = int(effect_str.split()[1])
        effects.append(DealDamageEffect(amount))
        return effects, False

    # 3. Draw cards
    if effect_str.lower().startswith("draw"):
        from axis3.engine.abilities.effects.draw import DrawCardEffect
        amount = int(effect_str.split()[1])
        effects.append(DrawCardEffect(amount))
        return effects, False

    # Default: no effect
    return [], False
