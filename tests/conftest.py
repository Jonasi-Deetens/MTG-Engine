import pytest
import itertools

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base  # adjust if your Base is elsewhere
from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics, Axis1ActivatedAbility
from axis2.builder import GameState as Axis2GameState
from axis2.builder import Axis2Builder
from axis2.schema import ContinuousEffect, ReplacementEffect
from axis3.state.game_state import GameState as Axis3GameState
from axis3.model.characteristics import PrintedCharacteristics as Characteristics
from axis3.state.objects import RuntimeObject
from axis3.state.zones import ZoneType

def pytest_addoption(parser):
    parser.addoption(
        "--name",
        action="store",
        default=None,
        help="Name of the card to debug in Axis2"
    )

@pytest.fixture
def card_name(request):
    return request.config.getoption("--name")


@pytest.fixture
def axis2_builder():
    return Axis2Builder

@pytest.fixture
def game_state():
    return Axis2GameState(
        active_player_id="P1",
        priority_player_id="P1",
        turn_phase="main",
        turn_step="precombat",
        battlefield=[],
        graveyards={"P1": [], "P2": []},
        hands={"P1": [], "P2": []},
        exile=[],
        command_zone=[],
        stack=[],
        continuous_effects=[],
        replacement_effects=[],
        global_restrictions=[],
    )

@pytest.fixture
def game_state_factory():
    _id_counter = itertools.count()

    def new_id():
        return f"obj_{next(_id_counter)}"

    def runtime_to_axis1_char(runtime_char: Characteristics):
        return Axis1Characteristics(
            mana_cost=runtime_char.mana_cost,
            mana_value=getattr(runtime_char, "mana_value", 0),
            colors=runtime_char.colors,
            color_identity=getattr(runtime_char, "colors", []),
            card_types=runtime_char.types,
            subtypes=runtime_char.subtypes,
            supertypes=runtime_char.supertypes,
            power=runtime_char.power,
            toughness=runtime_char.toughness,
            loyalty=runtime_char.loyalty,
        )

    def _factory(
        p0_cards=None,
        p1_cards=None,
        p0_hand=None,
        p1_hand=None,
        p0_library=None,
        p1_library=None,
    ):
        # Legacy compatibility
        if p0_hand is None:
            p0_hand = p0_cards or []
        if p1_hand is None:
            p1_hand = p1_cards or []

        # New optional library inputs
        p0_library = p0_library or []
        p1_library = p1_library or []

        game = Axis3GameState(
            players=[PlayerState(id=0), PlayerState(id=1)],
            objects={},
        )
        # Ensure Axis2Builder sees these
        game.global_restrictions = []
        game.continuous_effects = []
        game.replacement_effects = []

        def make_characteristics(name: str) -> Characteristics:
            # Special-case real land used in tests 
            if name == "Temple of Silence": 
                return Characteristics( 
                    name=name, 
                    mana_cost=None, 
                    types=["Land"], 
                    subtypes=[], 
                    supertypes=[], 
                    colors=[], 
                    power=None, 
                    toughness=None, 
                    loyalty=None, 
                )
            else:
                creature_stats = {
                    "Grizzly Bears": (2, 2),
                    "Hill Giant": (3, 3),
                    "Elvish Visionary": (1, 1),
                    "Wurmcoil Engine": (6, 6)
                }
                power, toughness = creature_stats.get(name, (None, None))
                
                types = ["Creature"] if name in creature_stats else ["Spell"]
                
                return Characteristics(
                    name=name,
                    mana_cost=None,
                    types=types,
                    subtypes=[],
                    supertypes=[],
                    colors=[],
                    power=power,
                    toughness=toughness,
                    loyalty=None
                )


        def add_cards(player_id, card_names, zone):
            for name in card_names:
                obj_id = new_id()
                char = make_characteristics(name)

                # Build Axis1 characteristics
                axis1_char = runtime_to_axis1_char(char)

                # ------------------------------------------------------------
                # HARDCODE REAL CARD DATA FOR TESTING
                # ------------------------------------------------------------
                if name == "Temple of Silence":
                    axis1_char.card_types = ["Land"]
                    axis1_char.subtypes = []
                    axis1_char.supertypes = []
                    axis1_face = Axis1Face(
                        name=name,
                        mana_cost="",
                        power=None,
                        toughness=None,
                        colors=[],
                        subtypes=[],
                        card_types=["Land"],
                        supertypes=[],
                        oracle_text=(
                            "This land enters tapped.\n"
                            "When this land enters, scry 1.\n"
                            "{T}: Add {W} or {B}."
                        ),
                        keywords=["Scry"],
                    )
                else:
                    # your existing logic
                    if "Creature" in axis1_char.card_types:
                        card_types = ["Creature"]
                    elif "Land" in axis1_char.card_types:
                        card_types = ["Land"]
                    elif "Enchantment" in axis1_char.card_types:
                        card_types = ["Enchantment"]
                    elif "Instant" in axis1_char.card_types:
                        card_types = ["Instant"]
                    else:
                        card_types = ["Spell"]

                    axis1_face = Axis1Face(
                        name=name,
                        mana_cost=char.mana_cost,
                        power=char.power,
                        toughness=char.toughness,
                        colors=char.colors,
                        subtypes=char.subtypes,
                        card_types=card_types,
                        supertypes=char.supertypes,
                        oracle_text="",
                        keywords=[],
                    )

                    if name == "Elvish Visionary":
                        axis1_face.oracle_text = "When Elvish Visionary enters the battlefield, draw a card."

                axis1_card = Axis1Card(
                    card_id=f"{name.lower()}-001",
                    oracle_id=f"{name.lower()}-oracle",
                    scryfall_id=f"{name.lower()}-scry",
                    layout="normal",
                    names=[name],
                    faces=[axis1_face],
                    characteristics=axis1_char,
                    rules_tags=[],
                    intrinsic_rules=[],
                    zones_allowed=["Library", "Hand", "Battlefield", "Graveyard", "Exile"],
                )

                # Build Axis2 object from Axis1
                axis2_card = Axis2Builder.build(axis1_card, game)
                # Inject test-only replacement effects
                if name == "Wurmcoil Engine":
                    axis2_card.replacement_effects.append(
                        ReplacementEffect(
                            type="dies_exile_instead",
                            subject="this",
                            event="die",
                            replacement="exile",
                            extra={}
                        )
                    )


                # Make sure these attributes exist
                axis2_card.triggers = getattr(axis2_card, "triggers", [])
                if not hasattr(axis2_card, "continuous_effects"):
                    axis2_card.continuous_effects = []
                if not hasattr(axis2_card, "replacement_effects"):
                    axis2_card.replacement_effects = []
                if name == "Glorious Anthem":
                    ce = ContinuousEffect(
                        kind="global_pt_modifier",
                        subject="creatures_you_control",
                        value={"power": 1, "toughness": 1},
                        layering="7b"
                    )
                    axis2_card.continuous_effects.append(ce)

                if name == "Holy Strength Aura":
                    ce = ContinuousEffect(
                        kind="aura_pt_and_ability",
                        subject="enchanted_creature",
                        value={
                            "power": 2,
                            "toughness": 2,
                            "abilities": ["flying"]
                        },
                        layering="7b",
                    )
                    axis2_card.continuous_effects.append(ce)

                                    
                # ETB trigger: draw a card
                if "etb_trigger" in axis1_card.rules_tags:
                    def etb_draw(gs, obj_id=obj_id):
                        draw_card(gs, gs.objects[obj_id].owner, 1)
                    axis2_card.triggers.append({
                        "event": "enter_battlefield",
                        "effect": etb_draw
                    })

                # Dies → Exile replacement
                if "dies_exile_instead" in axis1_card.rules_tags:
                    def dies_exile(obj, gs):
                        obj.zone = ZoneType.EXILE
                    axis2_card.replacement_effects.append({
                        "trigger": "dies",
                        "replacement": dies_exile
                    })


                # Wrap in RuntimeObject for Axis3
                obj = RuntimeObject(
                    id=obj_id,
                    owner=player_id,
                    controller=player_id,
                    zone=ZoneType.HAND if zone == "hand" else ZoneType.LIBRARY,
                    name=name,
                    axis1=axis1_card,
                    axis2=axis2_card,
                    characteristics=char,
                )

                game.objects[obj_id] = obj
                if zone == "hand": 
                    game.players[player_id].hand.append(obj_id) 
                elif zone == "library": 
                    game.players[player_id].library.append(obj_id) 
                else: 
                    raise ValueError(f"Unknown zone: {zone}")

        add_cards(0, p0_hand, zone="hand") 
        add_cards(0, p0_library, zone="library") 
        add_cards(1, p1_hand, zone="hand") 
        add_cards(1, p1_library, zone="library")

        return game

    return _factory
    
@pytest.fixture
def forest_axis1():
    return Axis1Card(
        card_id="forest-001",
        oracle_id="forest-oracle",
        scryfall_id="forest-scry",
        layout="normal",
        names=["Forest"],
        faces=[
            Axis1Face(
                name="Forest",
                mana_cost="",
                power=None,
                toughness=None,
                colors=[],
                subtypes=["Forest"],
                card_types=["Basic", "Land"],
                supertypes=["Basic"],
                oracle_text="({T}: Add {G}.)",
                keywords=[],
            )
        ],
        characteristics=Axis1Characteristics(
            mana_cost="",
            mana_value=0,
            colors=[],
            color_identity=["G"],
            card_types=["Basic", "Land"],
            subtypes=["Forest"],
            supertypes=["Basic"],
            power=None,
            toughness=None,
        ),
        rules_tags=[],
        intrinsic_rules=[],
        zones_allowed=["Library", "Hand", "Battlefield", "Graveyard", "Exile"],
    )

@pytest.fixture
def axis1_deck_p1(forest_axis1, hydra_axis1):
    # Repeat cards to make at least 7
    return [forest_axis1, hydra_axis1] * 4  # 8 cards

@pytest.fixture
def axis1_deck_p2(forest_axis1):
    return [forest_axis1] * 4  # 4 cards

@pytest.fixture
def hydra_axis1():
    return Axis1Card(
        card_id="hydra-001",
        oracle_id="hydra-oracle",
        scryfall_id="hydra-scry",
        layout="normal",
        names=["Whiptongue Hydra"],
        faces=[
            Axis1Face(
                name="Whiptongue Hydra",
                mana_cost="{5}{G}",
                power="4",
                toughness="4",
                colors=["G"],
                subtypes=["Lizard", "Hydra"],
                card_types=["Creature"],
                supertypes=[],
                oracle_text="Reach\nWhen this creature enters the battlefield, destroy all creatures with flying.",
                keywords=["Reach"],
                activated_abilities=[
                    Axis1ActivatedAbility(
                        raw="+1: Gain +1/+1 until end of turn.",
                        cost="+1",
                        cost_parts=[{"type": "mana", "amount": 1}],
                        effect="Gain +1/+1 until end of turn.",
                        cost_metadata={"mana": 1},
                        activation_conditions=[],
                    )
                ],
            )
        ],
        characteristics = Axis1Characteristics(
            mana_cost="{5}{G}",
            mana_value=6,
            colors=["G"],
            color_identity=["G"],
            card_types=["Creature"],
            subtypes=["Lizard", "Hydra"],
            supertypes=[],
            power="4",
            toughness="4",
            loyalty=None,
        ),
        rules_tags=["etb_trigger", "dies_exile_instead"],        
        intrinsic_rules=[],
        zones_allowed=["Library", "Hand", "Battlefield", "Graveyard", "Exile"],
    )


@pytest.fixture
def db_session():
    """Provide a fresh in-memory SQLite session for each test."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)

    # Create all tables
    Base.metadata.create_all(engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="session") 
def pg_engine(): 
    return create_engine("postgresql+psycopg2://postgres:postgres@localhost:5433/mtg")

@pytest.fixture
def pg_session(pg_engine):
    with pg_engine.connect() as conn:
        yield conn
