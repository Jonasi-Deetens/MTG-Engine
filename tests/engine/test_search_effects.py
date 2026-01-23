from engine import GameObject, GameState, PlayerState
from engine.effects import EffectResolver
from engine.state import ResolveContext
from engine.zones import ZONE_BATTLEFIELD, ZONE_LIBRARY


def test_search_filters_card_type_and_mana_value():
    player = PlayerState(id=0)
    game_state = GameState(players=[player])
    resolver = EffectResolver(game_state)
    creature = GameObject(
        id="creature",
        name="Creature A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_LIBRARY,
        mana_value=1,
    )
    artifact = GameObject(
        id="artifact",
        name="Artifact A",
        owner_id=0,
        controller_id=0,
        types=["Artifact"],
        zone=ZONE_LIBRARY,
        mana_value=3,
    )
    game_state.add_object(creature)
    game_state.add_object(artifact)
    player.library = [creature.id, artifact.id]

    context = ResolveContext(
        controller_id=0,
        targets={"search_results": [creature.id, artifact.id]},
    )
    result = resolver.apply(
        {
            "type": "search",
            "zone": "library",
            "cardType": "creature",
            "manaValueComparison": "<=",
            "manaValueComparisonValue": 2,
            "target": "player",
        },
        context,
    )

    assert result["found"] == [creature.id]


def test_search_different_name_excludes_controlled_names():
    player = PlayerState(id=0)
    game_state = GameState(players=[player])
    resolver = EffectResolver(game_state)
    controlled = GameObject(
        id="controlled",
        name="Same Name",
        owner_id=0,
        controller_id=0,
        types=["Enchantment"],
        zone=ZONE_BATTLEFIELD,
    )
    same_name = GameObject(
        id="same",
        name="Same Name",
        owner_id=0,
        controller_id=0,
        types=["Enchantment"],
        zone=ZONE_LIBRARY,
        mana_value=2,
    )
    different_name = GameObject(
        id="different",
        name="Different Name",
        owner_id=0,
        controller_id=0,
        types=["Enchantment"],
        zone=ZONE_LIBRARY,
        mana_value=2,
    )
    game_state.add_object(controlled)
    game_state.add_object(same_name)
    game_state.add_object(different_name)
    player.library = [same_name.id, different_name.id]

    context = ResolveContext(
        controller_id=0,
        targets={"search_results": [same_name.id, different_name.id]},
    )
    result = resolver.apply(
        {
            "type": "search",
            "zone": "library",
            "cardType": "enchantment",
            "differentName": {
                "enabled": True,
                "compareAgainstType": "enchantment",
                "compareAgainstZone": "controlled",
            },
            "target": "player",
        },
        context,
    )

    assert result["found"] == [different_name.id]


def test_search_different_name_compares_triggering_source():
    player = PlayerState(id=0)
    game_state = GameState(players=[player])
    resolver = EffectResolver(game_state)
    triggering = GameObject(
        id="triggering",
        name="Same Name",
        owner_id=0,
        controller_id=0,
        types=["Enchantment", "Aura"],
        zone=ZONE_BATTLEFIELD,
        mana_value=2,
    )
    same_name = GameObject(
        id="same",
        name="Same Name",
        owner_id=0,
        controller_id=0,
        types=["Enchantment", "Aura"],
        zone=ZONE_LIBRARY,
        mana_value=2,
    )
    different_name = GameObject(
        id="different",
        name="Different Name",
        owner_id=0,
        controller_id=0,
        types=["Enchantment", "Aura"],
        zone=ZONE_LIBRARY,
        mana_value=2,
    )
    game_state.add_object(triggering)
    game_state.add_object(same_name)
    game_state.add_object(different_name)
    player.library = [same_name.id, different_name.id]

    context = ResolveContext(
        controller_id=0,
        targets={"search_results": [same_name.id, different_name.id]},
        triggering_source_id=triggering.id,
    )
    result = resolver.apply(
        {
            "type": "search",
            "zone": "library",
            "cardType": "enchantment",
            "differentName": {
                "enabled": True,
                "compareAgainstType": "aura",
                "compareAgainstSource": "triggering_source",
            },
            "target": "player",
        },
        context,
    )

    assert result["found"] == [different_name.id]

