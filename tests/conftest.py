import pytest
import itertools

from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics
from axis2.builder import Axis2Builder
from axis2.schema import Axis2Card
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
    """
    Expose the Axis2Builder for tests.
    """
    return Axis2Builder


@pytest.fixture
def axis2_card_factory():
    """
    Creates Axis1Cards and compiles them into Axis2Cards.
    Pure Axis2. No Axis3. No runtime.
    """

    _id_counter = itertools.count()

    def new_id():
        return f"card_{next(_id_counter)}"

    def make_axis1_card(
        name: str,
        oracle_text: str = "",
        types=None,
        power=None,
        toughness=None,
        mana_cost=None,
        colors=None,
        subtypes=None,
        supertypes=None,
    ):
        types = types or []
        colors = colors or []
        subtypes = subtypes or []
        supertypes = supertypes or []

        # Axis1Characteristics
        axis1_char = Axis1Characteristics(
            mana_cost=mana_cost,
            mana_value=0,
            colors=colors,
            color_identity=colors,
            card_types=types,
            subtypes=subtypes,
            supertypes=supertypes,
            power=power,
            toughness=toughness,
            loyalty=None,
            defense=None,
        )

        # Axis1Face
        face = Axis1Face(
            name=name,
            mana_cost=mana_cost,
            power=power,
            toughness=toughness,
            colors=colors,
            subtypes=subtypes,
            card_types=types,
            supertypes=supertypes,
            oracle_text=oracle_text,
            keywords=[],
        )

        # Axis1Card
        axis1_card = Axis1Card(
            card_id=new_id(),
            oracle_id=f"{name.lower()}-oracle",
            scryfall_id=f"{name.lower()}-scry",
            layout="normal",
            names=[name],
            faces=[face],
            characteristics=axis1_char,
            rules_tags=[],
            intrinsic_rules=[],
            zones_allowed=["Library", "Hand", "Battlefield", "Graveyard", "Exile"],
        )

        # Compile to Axis2
        axis2_card = Axis2Builder.build(axis1_card)

        return axis1_card, axis2_card

    return make_axis1_card

# ------------------------------------------------------------
# BASIC AXIS1 CARD FIXTURES
# ------------------------------------------------------------

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
            loyalty=None,
            defense=None,
        ),
        rules_tags=[],
        intrinsic_rules=[],
        zones_allowed=["Library", "Hand", "Battlefield", "Graveyard", "Exile"],
    )


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
                oracle_text=(
                    "Reach\n"
                    "When this creature enters the battlefield, destroy all creatures with flying."
                ),
                keywords=["Reach"],
                activated_abilities=[
                    Axis1ActivatedAbility(
                        raw="+1: Gain +1/+1 until end of turn.",
                        cost="+1",
                        cost_parts=[{"raw": "+1", "metadata": {}}],
                        effect="Gain +1/+1 until end of turn.",
                        cost_metadata={"loyalty": 1},
                        activation_conditions=[],
                    )
                ],
            )
        ],
        characteristics=Axis1Characteristics(
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
            defense=None,
        ),
        rules_tags=[],
        intrinsic_rules=[],
        zones_allowed=["Library", "Hand", "Battlefield", "Graveyard", "Exile"],
    )


# ------------------------------------------------------------
# SIMPLE DECK FIXTURES (Axis1 only)
# ------------------------------------------------------------

@pytest.fixture
def axis1_deck_p1(forest_axis1, hydra_axis1):
    return [forest_axis1, hydra_axis1] * 4  # 8 cards


@pytest.fixture
def axis1_deck_p2(forest_axis1):
    return [forest_axis1] * 4


# ------------------------------------------------------------
# DATABASE FIXTURES (unchanged)
# ------------------------------------------------------------

@pytest.fixture
def db_session():
    """Provide a fresh in-memory SQLite session for each test."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)

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
