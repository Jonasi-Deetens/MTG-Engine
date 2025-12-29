# src/axis3/translate/activated_builder.py

from axis3.abilities.activated import RuntimeActivatedAbility
from axis3.engine.stack.item import StackItem
from axis3.state.objects import RuntimeObject
from axis3.state.game_state import GameState

def register_runtime_activated_abilities(game_state: GameState, rt_obj: RuntimeObject):
    axis2 = getattr(rt_obj, "axis2_card", None)
    if not axis2:
        return

    rt_obj.runtime_activated_abilities = []

    for aa in getattr(axis2, "activated_abilities", []):
        is_mana_ability = getattr(aa, "is_mana_ability", False)

        # Wrap effect directly (does NOT push itself)
        def make_effect(aa=aa):
            def effect(gs: GameState):
                aa.effect(gs, rt_obj.id, rt_obj.controller)
            return effect

        raa = RuntimeActivatedAbility(
            source_id=rt_obj.id,
            controller=rt_obj.controller,
            cost=getattr(aa, "cost", None),
            effect=make_effect()
        )
        raa.is_mana_ability = is_mana_ability

        # Override activate to push the StackItem (unless it's a mana ability)
        def make_activate(raa=raa):
            def activate(gs: GameState):
                if raa.is_mana_ability:
                    # resolve immediately
                    raa.effect(gs)
                else:
                    # push to stack for later resolution
                    gs.stack.push(StackItem(activated_ability=raa))
                return True
            return activate

        raa.activate = make_activate()
        raa.invoke = raa.activate  # convenience

        rt_obj.runtime_activated_abilities.append(raa)
