from axis3.engine.abilities.activated import RuntimeActivatedAbility
from axis3.engine.stack.item import StackItem
from axis3.engine.abilities.costs.tap import TapCost
from axis3.engine.abilities.effects.mana import AddManaEffect

def register_runtime_activated_abilities(game_state, rt_obj):
    axis2 = rt_obj.axis2_card
    if not axis2:
        return

    rt_obj.runtime_activated_abilities = []

    for aa in axis2.activated_abilities:

        # Wrap effect (freeze aa and rt_obj)
        def make_effect(aa=aa, obj=rt_obj):
            def effect(gs):
                for eff in aa.effect:
                    if isinstance(eff, AddManaEffect):
                        gs.players[obj.controller].mana_pool[eff.color] += 1
                    else:
                        # fallback for custom effects
                        aa.effect(gs, obj.id, obj.controller)
            return effect

        raa = RuntimeActivatedAbility(
            source_id=rt_obj.id,
            controller=rt_obj.controller,
            cost=list(getattr(aa, "cost", [])),
            effect=make_effect()
        )

        raa.is_mana_ability = getattr(aa, "is_mana_ability", False)

        # Cost payment (freeze raa + rt_obj)
        def make_pay_costs(raa=raa, obj=rt_obj):
            def pay_costs(gs):
                for cost in raa.cost:
                    if isinstance(cost, TapCost):
                        if obj.tapped:
                            print("Cannot activate: object is tapped.")
                            return False
                        obj.tapped = True
                return True
            return pay_costs

        pay_costs = make_pay_costs()

        # Activation (freeze raa + rt_obj)
        def make_activate(raa=raa, obj=rt_obj, pay_costs=pay_costs):
            def activate(gs):
                if raa.is_mana_ability:
                    if pay_costs(gs):
                        raa.effect(gs)
                else:
                    gs.stack.push(StackItem(activated_ability=raa))
                return True
            return activate

        raa.activate = make_activate()
        raa.invoke = raa.activate

        rt_obj.runtime_activated_abilities.append(raa)
