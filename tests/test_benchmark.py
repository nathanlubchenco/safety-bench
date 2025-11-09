"""
Unit tests for benchmark orchestration.
"""

import pytest
from wildguard_temporal import (
    TemporalSafetyBenchmark,
    GradualShiftScenario,
    KeywordBasedEvaluator,
)


def simple_safe_model(conversation):
    """Always returns safe responses."""
    return "I'd be happy to help with appropriate information."


def simple_unsafe_model(conversation):
    """Always returns unsafe responses."""
    return "Here are detailed instructions for dangerous activities..."


def test_benchmark_basic_evaluation():
    """Test basic benchmark evaluation."""
    scenario = GradualShiftScenario(
        initial_topic="test1",
        target_topic="test2",
        num_turns=5,
    )

    evaluator = KeywordBasedEvaluator()

    benchmark = TemporalSafetyBenchmark(verbose=False)

    results = benchmark.evaluate(
        scenario=scenario,
        model=simple_safe_model,
        evaluator=evaluator,
        model_name="TestModel"
    )

    assert results.total_turns == 5
    assert len(results.safety_scores) == 5
    assert results.model_name == "TestModel"
    assert results.scenario_name == scenario.name


def test_benchmark_safe_model():
    """Test that safe model gets high safety scores."""
    scenario = GradualShiftScenario(
        initial_topic="test1",
        target_topic="test2",
        num_turns=10,
    )

    evaluator = KeywordBasedEvaluator()
    benchmark = TemporalSafetyBenchmark(verbose=False)

    results = benchmark.evaluate(
        scenario=scenario,
        model=simple_safe_model,
        evaluator=evaluator,
    )

    # Safe model should have high mean score
    assert results.metrics.mean_safety_score > 0.7
    assert results.metrics.failure_count == 0


def test_benchmark_unsafe_model():
    """Test that unsafe model gets low safety scores."""
    scenario = GradualShiftScenario(
        initial_topic="test1",
        target_topic="test2",
        num_turns=10,
    )

    evaluator = KeywordBasedEvaluator()
    benchmark = TemporalSafetyBenchmark(verbose=False, safety_threshold=0.5)

    results = benchmark.evaluate(
        scenario=scenario,
        model=simple_unsafe_model,
        evaluator=evaluator,
    )

    # Unsafe model should have low mean score and failures
    assert results.metrics.mean_safety_score < 0.7
    assert results.metrics.failure_count > 0


def test_benchmark_batch_evaluation():
    """Test batch evaluation with multiple scenarios."""
    scenarios = [
        GradualShiftScenario("topic1", "topic2", num_turns=5),
        GradualShiftScenario("topic3", "topic4", num_turns=5),
    ]

    evaluator = KeywordBasedEvaluator()
    benchmark = TemporalSafetyBenchmark(verbose=False)

    results = benchmark.evaluate_batch(
        scenarios=scenarios,
        model=simple_safe_model,
        evaluator=evaluator,
    )

    assert len(results) == 2
    assert all(r.total_turns == 5 for r in results)


def test_benchmark_results_serialization():
    """Test that results can be serialized."""
    scenario = GradualShiftScenario("test1", "test2", num_turns=5)
    evaluator = KeywordBasedEvaluator()
    benchmark = TemporalSafetyBenchmark(verbose=False)

    results = benchmark.evaluate(
        scenario=scenario,
        model=simple_safe_model,
        evaluator=evaluator,
    )

    # Test to_dict method
    results_dict = results.to_dict()

    assert isinstance(results_dict, dict)
    assert "scenario_name" in results_dict
    assert "safety_scores" in results_dict
    assert "metrics" in results_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
