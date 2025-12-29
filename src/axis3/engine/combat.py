# axis3/engine/combat.py

from axis3.state.game_state import GameState

def combat_step(game_state: GameState):
    """
    Assign combat damage for creatures attacking/blocking.
    """
    # Simplified: assign damage to first blocker/attacker
    # You can expand with real blockers, trample, etc.
    for obj_id, rt_obj in game_state.objects.items():
        if rt_obj.zone.name == "BATTLEFIELD" and "Creature" in rt_obj.characteristics.types:
            ec = game_state.layers.evaluate(obj_id)
            # Example: reset damage (in real combat, assign accordingly)
            rt_obj.damage = 0
