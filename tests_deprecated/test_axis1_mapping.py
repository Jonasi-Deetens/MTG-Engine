import pytest
from scryfall.mappers.axis1_mapper import Axis1Mapper
from axis1.schema import Axis1Card


def test_map_basic_creature_card():
    scry_json = {
        "id": "123",
        "oracle_id": "oracle-123",
        "name": "Elf Druid",
        "layout": "normal",
        "mana_cost": "{1}{G}",
        "cmc": 2.0,
        "colors": ["G"],
        "color_identity": ["G"],
        "type_line": "Legendary Creature — Elf Druid",
        "power": "2",
        "toughness": "2",
        "loyalty": None,
        "defense": None,
        "oracle_text": "Some rules text.",
        "keywords": ["Reach"],
        "rarity": "rare",
        "artist": "Cool Artist",
        "illustration_id": "ill-1",
        "frame": "2015",
        "border_color": "black",
        "watermark": None,
        "legalities": {"modern": "legal"},
        "image_uris": {"normal": "http://example.com/card.png"},
        "set": "ABC",
        "collector_number": "123",
        "lang": "en",
    }

    mapper = Axis1Mapper()
    card: Axis1Card = mapper.map(scry_json)

    assert card.card_id == "123"
    assert card.oracle_id == "oracle-123"
    assert card.layout == "normal"
    assert card.characteristics.mana_cost == "{1}{G}"
    assert card.characteristics.mana_value == 2.0
    assert card.characteristics.colors == ["G"]
    assert "Creature" in card.characteristics.card_types
    assert "Elf" in card.characteristics.subtypes
    assert card.faces[0].name == "Elf Druid"
    assert card.faces[0].oracle_text == "Some rules text."
    assert card.metadata.rarity == "rare"
    assert card.metadata.artist == "Cool Artist"
    assert card.metadata.image_uris["normal"] == "http://example.com/card.png"
