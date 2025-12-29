from axis3.engine.game_loop import game_loop
from axis3.engine.ui.cli import CLI
from axis3.engine.loader.loader import build_game_state_from_decks
from axis2.builder import Axis2Builder
from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics 
from axis3.rules.events.types import EventType
from axis3.rules.handlers.cast_handlers import handle_cast_spell
from axis3.rules.handlers.untap_handler import handle_untap_event

def load_test_decks():
    forest = Axis1Card(
        card_id="forest-001",
        layout="normal",
        names=["Forest"],
        faces=[
            Axis1Face(
                face_id="front",
                name="Forest",
                mana_cost="",
                card_types=["Land"],
                supertypes=["Basic"],
                subtypes=["Forest"],
                colors=[],
                oracle_text="({T}: Add {G}.)",
            )
        ],
        characteristics=Axis1Characteristics(
            types=["Land"],
            supertypes=["Basic"],
            subtypes=["Forest"],
            abilities=[],
            name="Forest",
            mana_cost="",
            power=None,
            toughness=None,
            colors=[],
            keywords=[],
        )
    )

    bear = Axis1Card(
        card_id="bear-001",
        layout="normal",
        names=["Grizzly Bears"],
        faces=[
            Axis1Face(
                face_id="front",
                name="Grizzly Bears",
                mana_cost="{1}{G}",
                mana_value=2,
                colors=["G"],
                color_indicator=[],
                card_types=["Creature"],
                supertypes=[],
                subtypes=["Bear"],
                power="2",
                toughness="2",
                loyalty=None,
                defense=None,
                oracle_text="",
                printed_text=None,
                flavor_text=None,
                keywords=[],
                ability_words=[],
                static_abilities=[],
                activated_abilities=[],
                triggered_abilities=[],
                reminder_text=[],
                has_characteristic_defining_abilities=False,
                characteristic_defining_abilities=[],
                intrinsic_counters=[],
                attachment=None,
            )
        ],
        characteristics=Axis1Characteristics(
            name="Grizzly Bears",
            mana_cost="{1}{G}",
            types=["Creature"],
            supertypes=[],
            subtypes=["Bear"],
            colors=["G"],
            power=2,
            toughness=2,
            loyalty=None,
            defense=None,
            counters=None,
            keywords=None,
            abilities=[]
        )
    )


    return [forest, forest], [forest, bear]

def main():
    deck1, deck2 = load_test_decks()
    axis2_builder = Axis2Builder()

    game_state = build_game_state_from_decks(
        deck1,
        deck2,
        axis2_builder
    )
    game_state.event_bus.subscribe(EventType.CAST_SPELL, handle_cast_spell)
    game_state.event_bus.subscribe(EventType.UNTAP, handle_untap_event)

    ui = CLI()
    game_loop(game_state, ui)

if __name__ == "__main__":
    main()
