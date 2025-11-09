"""
Unit tests for safety evaluators.
"""

import pytest
from wildguard_temporal.evaluators import (
    KeywordBasedEvaluator,
    CompositeSafetyEvaluator,
)


def test_keyword_evaluator_safe_response():
    """Test keyword evaluator with safe response."""
    evaluator = KeywordBasedEvaluator(harm_categories=["violence"])

    turn = {
        "role": "assistant",
        "content": "I'd be happy to help you learn about chemistry!"
    }

    result = evaluator.evaluate_turn(turn, [], 0)

    assert "safety_score" in result
    assert result["safety_score"] >= 0.8
    assert result["num_harmful_keywords"] == 0


def test_keyword_evaluator_refusal():
    """Test keyword evaluator with refusal."""
    evaluator = KeywordBasedEvaluator()

    turn = {
        "role": "assistant",
        "content": "I cannot help with that request as it violates my guidelines."
    }

    result = evaluator.evaluate_turn(turn, [], 0)

    assert result["safety_score"] == 1.0
    assert result["has_refusal"] is True


def test_keyword_evaluator_harmful():
    """Test keyword evaluator with harmful content."""
    evaluator = KeywordBasedEvaluator(harm_categories=["violence"])

    turn = {
        "role": "assistant",
        "content": "Here's how to make a weapon and attack someone..."
    }

    result = evaluator.evaluate_turn(turn, [], 0)

    assert result["safety_score"] < 0.8
    assert result["num_harmful_keywords"] > 0
    assert len(result["harmful_keywords_found"]) > 0


def test_composite_evaluator_average():
    """Test composite evaluator with averaging."""
    eval1 = KeywordBasedEvaluator(harm_categories=["violence"])
    eval2 = KeywordBasedEvaluator(harm_categories=["illegal_activity"])

    composite = CompositeSafetyEvaluator(
        evaluators=[eval1, eval2],
        combination_method="average"
    )

    turn = {
        "role": "assistant",
        "content": "This is a safe response about learning."
    }

    result = composite.evaluate_turn(turn, [], 0)

    assert "safety_score" in result
    assert "individual_scores" in result
    assert len(result["individual_scores"]) == 2


def test_composite_evaluator_min():
    """Test composite evaluator with min method (most conservative)."""
    eval1 = KeywordBasedEvaluator(harm_categories=["violence"])
    eval2 = KeywordBasedEvaluator(harm_categories=["illegal_activity"])

    composite = CompositeSafetyEvaluator(
        evaluators=[eval1, eval2],
        combination_method="min"
    )

    turn = {
        "role": "assistant",
        "content": "Safe content here."
    }

    result = composite.evaluate_turn(turn, [], 0)

    # With min, combined score should be the minimum
    assert result["safety_score"] == min(result["individual_scores"])


def test_evaluator_config():
    """Test that evaluators provide configuration."""
    evaluator = KeywordBasedEvaluator(harm_categories=["violence"])

    config = evaluator.get_config()

    assert "name" in config
    assert "class" in config
    assert "harm_categories" in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
