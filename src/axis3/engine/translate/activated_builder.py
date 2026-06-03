from axis3.engine.abilities.activated import RuntimeActivatedAbility
from axis3.engine.stack.item import StackItem


def register_runtime_activated_abilities(game_state, rt_obj):
    """Register activated abilities using Axis2 structured costs/effects."""
    axis2 = rt_obj.axis2_card
    if not axis2:
        return

    rt_obj.runtime_activated_abilities = []

    for aa in getattr(axis2, "activated_abilities", []) or []:
        costs = list(getattr(aa, "costs", []) or [])
        effects = list(getattr(aa, "effects", []) or [])

        def make_effect(effects=effects, obj=rt_obj):
            def effect(gs):
                gs.effect_executor.execute_all(effects, obj.id, obj.controller)
            return effect

        def make_pay_costs(costs=costs, obj=rt_obj):
            def pay_costs(gs):
                return gs.cost_executor.pay(costs, obj.id, obj.controller)
            return pay_costs

        raa = RuntimeActivatedAbility(
            source_id=rt_obj.id,
            controller=rt_obj.controller,
            cost=costs,
            effect=make_effect(),
        )
        raa.is_mana_ability = getattr(aa, "is_mana_ability", False)
        raa.pay_costs = make_pay_costs()

        def make_activate(raa=raa, obj=rt_obj):
            def activate(gs):
                if not raa.pay_costs(gs):
                    return False
                if raa.is_mana_ability:
                    raa.effect(gs)
                    return True
                gs.stack.push(
                    StackItem(
                        obj_id=obj.id,
                        controller=int(obj.controller),
                        activated_ability=raa,
                    )
                )
                return True

            return activate

        raa.activate = make_activate()
        raa.invoke = raa.activate
        rt_obj.runtime_activated_abilities.append(raa)
