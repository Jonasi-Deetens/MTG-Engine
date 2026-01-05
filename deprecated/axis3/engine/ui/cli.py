# axis3/engine/ui/cli.py

from .interface import UIInterface
from .actions import PlayerAction
from axis3.engine.actions.pass_action import PassAction
from axis3.engine.actions.play_land import PlayLandAction
from axis3.engine.actions.cast_spell import CastSpellAction
from axis3.engine.actions.activate_ability import ActivateAbilityAction


class CLI(UIInterface):
    """
    Minimal CLI UI for Axis3.
    Works with the engine loop and TurnManager.
    """

    def render(self, gs, tm):
        print("\n" + "=" * 50)
        print(f"TURN {tm.state.turn_number}")
        print(f"Active Player: {tm.active_player}")
        print(f"Priority: Player {tm.priority_player}")
        print(f"Phase: {tm.phase.name}  |  Step: {tm.step.name}")
        print("=" * 50)

        print("\n--- Battlefield ---")
        for obj in gs.objects.values():
            if obj.zone.name == "BATTLEFIELD":
                print(f"  {obj.id}: {obj.name} "
                      f"(tapped={obj.tapped}, dmg={obj.damage})")

        print("\n--- Stack ---")
        if gs.stack.is_empty():
            print("  <empty>")
        else:
            for i, item in enumerate(gs.stack.items):
                print(f"  {i}: {item}")

        print("\n--- Hand (P0) ---")
        p0 = gs.players[0]
        print("  " + ", ".join(p0.hand) if p0.hand else "  <empty>")

        print("\n--- Hand (P1) ---")
        p1 = gs.players[1]
        print("  " + ", ".join(p1.hand) if p1.hand else "  <empty>")

        print("\n")
        print(f"Mana Pool (P0): {gs.players[0].mana_pool}")
        print(f"Mana Pool (P1): {gs.players[1].mana_pool}")


    def get_player_action(self, player_id):
        cmd = input(f"Player {player_id} > ").strip().lower()

        if cmd == "pass":
            return PassAction(player_id)

        if cmd.startswith("playland "):
            _, card_id = cmd.split(maxsplit=1)
            return PlayLandAction(player_id, card_id)

        if cmd.startswith("cast "):
            _, card_id = cmd.split(maxsplit=1)
            return CastSpellAction(player_id, card_id)

        if cmd.startswith("activate "):
            _, rest = cmd.split(maxsplit=1)
            obj_id, ability_index = rest.split(":")
            return ActivateAbilityAction(player_id, obj_id, int(ability_index))

        print("Unknown command.")
        return None
