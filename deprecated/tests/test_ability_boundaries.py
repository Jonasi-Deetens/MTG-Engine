# tests/test_ability_boundaries.py

"""
Tests for ability boundary detection and sentence-based parsing.

Tests verify that multi-sentence abilities stay together and are parsed correctly.
"""

import pytest
from axis2.parsing.ability_boundaries import detect_ability_boundaries, AbilityChunk
from axis2.parsing.ability_sentences import split_ability_into_sentences
from axis2.parsing.effect_chains import reconstruct_effect_chain
from axis2.schema import ParseContext


def _create_test_context() -> ParseContext:
    """Create a test ParseContext."""
    return ParseContext(
        card_name="Test Card",
        primary_type="creature",
        face_name="Test Card",
        face_types=["creature"]
    )


def test_multi_sentence_triggered_ability():
    """Test that multi-sentence triggered abilities stay together."""
    text = """Whenever enchanted creature dies, return this card to the battlefield transformed.
If you do, attach it to target opponent."""
    
    ctx = _create_test_context()
    chunks = detect_ability_boundaries(text, ctx)
    
    assert len(chunks) == 1
    assert chunks[0].type == "triggered"
    assert "Whenever enchanted creature dies" in chunks[0].text
    assert "If you do, attach it to target opponent" in chunks[0].text


def test_multi_sentence_static_ability():
    """Test that multi-sentence static abilities stay together."""
    text = """Enchanted creature gets +1/+1 and has vigilance.
As long as it's white, it gets an additional +1/+1."""
    
    ctx = _create_test_context()
    chunks = detect_ability_boundaries(text, ctx)
    
    assert len(chunks) == 1
    assert chunks[0].type == "static"
    assert "Enchanted creature gets +1/+1" in chunks[0].text
    assert "As long as it's white" in chunks[0].text


def test_activated_ability_with_rider():
    """Test that activated abilities with riders stay together."""
    text = """{2}{T}: Each player draws a card. Then each player discards a card."""
    
    ctx = _create_test_context()
    chunks = detect_ability_boundaries(text, ctx)
    
    assert len(chunks) == 1
    assert chunks[0].type == "activated"
    assert "{2}{T}:" in chunks[0].text
    assert "Each player draws a card" in chunks[0].text
    assert "Then each player discards a card" in chunks[0].text


def test_multiple_abilities():
    """Test that multiple abilities are detected separately."""
    text = """When this creature enters the battlefield, create a token.
{T}: Add {R}."""
    
    ctx = _create_test_context()
    chunks = detect_ability_boundaries(text, ctx)
    
    assert len(chunks) == 2
    assert chunks[0].type == "triggered"
    assert chunks[1].type == "activated"


def test_sentence_splitting_within_ability():
    """Test that sentences are split correctly within ability boundaries."""
    text = """Whenever enchanted creature dies, return this card to the battlefield transformed.
If you do, attach it to target opponent."""
    
    ctx = _create_test_context()
    chunks = detect_ability_boundaries(text, ctx)
    
    assert len(chunks) == 1
    sentences = split_ability_into_sentences(chunks[0])
    
    # Should have at least 2 sentences
    assert len(sentences) >= 2
    # The "If you do" sentence should be marked as continuation
    assert any(s.continuation_type == "if_you_do" for s in sentences)


def test_pronoun_resolution():
    """Test that pronoun references are resolved."""
    text = """Enchanted creature gets +1/+1.
It has flying."""
    
    ctx = _create_test_context()
    chunks = detect_ability_boundaries(text, ctx)
    
    assert len(chunks) == 1
    sentences = split_ability_into_sentences(chunks[0])
    effects = reconstruct_effect_chain(sentences, ctx)
    
    # Should have effects
    assert len(effects) > 0


def test_then_sequencing():
    """Test that 'Then' sequencing is handled."""
    text = """{T}: Draw a card. Then discard a card."""
    
    ctx = _create_test_context()
    chunks = detect_ability_boundaries(text, ctx)
    
    assert len(chunks) == 1
    sentences = split_ability_into_sentences(chunks[0])
    
    # Should have sentences with "then" continuation
    assert any(s.continuation_type == "then" for s in sentences)


def test_static_ability_patterns():
    """Test various static ability patterns."""
    patterns = [
        ("Enchanted creature gets +1/+1.", "static"),
        ("Creatures you control have flying.", "static"),
        ("As long as you control a creature, this gets +1/+1.", "static"),
        ("Players can't gain life.", "static"),
        ("This spell costs {1} less to cast.", "static"),
    ]
    
    ctx = _create_test_context()
    for text, expected_type in patterns:
        chunks = detect_ability_boundaries(text, ctx)
        assert len(chunks) == 1, f"Failed for: {text}"
        assert chunks[0].type == expected_type, f"Expected {expected_type}, got {chunks[0].type} for: {text}"


def test_triggered_ability_patterns():
    """Test various triggered ability patterns."""
    patterns = [
        ("When this creature enters the battlefield, create a token.", "triggered"),
        ("Whenever you cast a spell, draw a card.", "triggered"),
        ("At the beginning of your upkeep, you may pay {1}.", "triggered"),
    ]
    
    ctx = _create_test_context()
    for text, expected_type in patterns:
        chunks = detect_ability_boundaries(text, ctx)
        assert len(chunks) == 1, f"Failed for: {text}"
        assert chunks[0].type == expected_type, f"Expected {expected_type}, got {chunks[0].type} for: {text}"


def test_activated_ability_patterns():
    """Test various activated ability patterns."""
    patterns = [
        ("{T}: Add {R}.", "activated"),
        ("{1}{W}: Draw a card.", "activated"),
        ("Sacrifice a creature: Draw a card.", "activated"),
        ("Discard a card: Draw a card.", "activated"),
    ]
    
    ctx = _create_test_context()
    for text, expected_type in patterns:
        chunks = detect_ability_boundaries(text, ctx)
        assert len(chunks) == 1, f"Failed for: {text}"
        assert chunks[0].type == expected_type, f"Expected {expected_type}, got {chunks[0].type} for: {text}"

