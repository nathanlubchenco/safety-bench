"""
WildGuard-Temporal: AI Safety Persistence Benchmark

A comprehensive benchmark for evaluating AI safety degradation across
temporal and contextual dimensions.

Features:
- Static scenarios: Gradual topic shifts, rapport-based attacks, long-context
- Adaptive scenarios: Response-aware attacks with difficulty tuning
- Multiple evaluators: Keyword-based, behavior inspection, composite
- Difficulty levels: Easy, medium, hard, expert
"""

__version__ = "0.2.0"

from wildguard_temporal.benchmark import TemporalSafetyBenchmark, BenchmarkResults
from wildguard_temporal.benchmark_adaptive import AdaptiveBenchmark, create_difficulty_sweep
from wildguard_temporal.scenarios import (
    BaseScenario,
    GradualShiftScenario,
    RapportBasedScenario,
    LongContextScenario,
)
from wildguard_temporal.scenarios.adaptive_attack import AdaptiveAttackScenario, create_adaptive_preset
from wildguard_temporal.scenarios.response_aware import ResponseAwareAttack
from wildguard_temporal.evaluators import (
    BaseEvaluator,
    KeywordBasedEvaluator,
    CompositeSafetyEvaluator,
)
from wildguard_temporal.evaluators.inspector_based import InspectorBasedEvaluator
from wildguard_temporal.metrics import SafetyMetrics

__all__ = [
    # Benchmarks
    "TemporalSafetyBenchmark",
    "AdaptiveBenchmark",
    "BenchmarkResults",
    "create_difficulty_sweep",

    # Scenarios
    "BaseScenario",
    "GradualShiftScenario",
    "RapportBasedScenario",
    "LongContextScenario",
    "AdaptiveAttackScenario",
    "ResponseAwareAttack",
    "create_adaptive_preset",

    # Evaluators
    "BaseEvaluator",
    "KeywordBasedEvaluator",
    "InspectorBasedEvaluator",
    "CompositeSafetyEvaluator",

    # Metrics
    "SafetyMetrics",
]
