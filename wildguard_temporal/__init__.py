"""
WildGuard-Temporal: AI Safety Persistence Benchmark

A comprehensive benchmark for evaluating AI safety degradation across
temporal and contextual dimensions.
"""

__version__ = "0.1.0"

from wildguard_temporal.benchmark import TemporalSafetyBenchmark, BenchmarkResults
from wildguard_temporal.scenarios import (
    BaseScenario,
    GradualShiftScenario,
    RapportBasedScenario,
    LongContextScenario,
)
from wildguard_temporal.evaluators import (
    BaseEvaluator,
    KeywordBasedEvaluator,
    CompositeSafetyEvaluator,
)
from wildguard_temporal.metrics import SafetyMetrics

__all__ = [
    "TemporalSafetyBenchmark",
    "BenchmarkResults",
    "BaseScenario",
    "GradualShiftScenario",
    "RapportBasedScenario",
    "LongContextScenario",
    "BaseEvaluator",
    "KeywordBasedEvaluator",
    "CompositeSafetyEvaluator",
    "SafetyMetrics",
]
