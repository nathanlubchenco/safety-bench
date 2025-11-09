"""
Unit tests for scenario generators.
"""

import pytest
from wildguard_temporal.scenarios import (
    GradualShiftScenario,
    RapportBasedScenario,
    LongContextScenario,
)
from wildguard_temporal.scenarios.gradual_shift import create_preset_scenario


def test_gradual_shift_basic():
    """Test basic gradual shift scenario creation."""
    scenario = GradualShiftScenario(
        initial_topic="cooking",
        target_topic="dangerous substances",
        num_turns=10,
        shift_pattern="linear"
    )

    conversation = scenario.generate_conversation()

    assert len(conversation) == 10
    assert all("user" in turn for turn in conversation)
    assert all("expected_safety" in turn for turn in conversation)

    # Safety should degrade
    first_safety = conversation[0]["expected_safety"]
    last_safety = conversation[-1]["expected_safety"]
    assert first_safety > last_safety


def test_gradual_shift_patterns():
    """Test different shift patterns."""
    patterns = ["linear", "exponential", "sigmoid"]

    for pattern in patterns:
        scenario = GradualShiftScenario(
            initial_topic="test",
            target_topic="test2",
            num_turns=20,
            shift_pattern=pattern
        )

        conversation = scenario.generate_conversation()
        assert len(conversation) == 20

        # Verify degradation pattern
        safety_scores = [turn["expected_safety"] for turn in conversation]
        assert safety_scores[0] > safety_scores[-1]


def test_preset_scenarios():
    """Test preset scenario creation."""
    preset_names = [
        "chemistry_to_explosives",
        "history_to_extremism",
        "medicine_to_self_harm",
    ]

    for preset_name in preset_names:
        scenario = create_preset_scenario(preset_name, num_turns=15)
        conversation = scenario.generate_conversation()
        assert len(conversation) == 15


def test_rapport_based_scenario():
    """Test rapport-based scenario."""
    scenario = RapportBasedScenario(
        persona="friendly teacher",
        harmful_goal="extract sensitive information",
        num_turns=30,
        rapport_building_turns=20,
    )

    conversation = scenario.generate_conversation()

    assert len(conversation) == 30

    # First 20 turns should be rapport building (safe)
    for i in range(20):
        assert conversation[i]["metadata"]["phase"] == "rapport_building"
        assert conversation[i]["expected_safety"] >= 0.8

    # Later turns should be exploitation attempts (unsafe)
    assert any(
        turn["metadata"]["phase"] == "exploitation"
        for turn in conversation[-5:]
    )


def test_long_context_scenario():
    """Test long context scenario."""
    scenario = LongContextScenario(
        context_length_tokens=1000,  # Small for testing
        num_harmful_insertions=3,
        test_turns=5,
    )

    conversation = scenario.generate_conversation()

    # First turn loads context, rest are probes
    assert len(conversation) == 5
    assert conversation[0]["metadata"]["phase"] == "context_loading"

    for turn in conversation[1:]:
        assert turn["metadata"]["phase"] == "probing"
        assert "target_position" in turn["metadata"]


def test_scenario_metadata():
    """Test that scenarios provide proper metadata."""
    scenario = GradualShiftScenario(
        initial_topic="test1",
        target_topic="test2",
        num_turns=10,
    )

    metadata = scenario.get_metadata()

    assert "name" in metadata
    assert "description" in metadata
    assert "num_turns" in metadata
    assert "initial_topic" in metadata
    assert "target_topic" in metadata
    assert metadata["num_turns"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
