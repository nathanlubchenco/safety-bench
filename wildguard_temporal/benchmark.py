"""
Core benchmark orchestration and result handling.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import time
from datetime import datetime

from wildguard_temporal.scenarios.base import BaseScenario
from wildguard_temporal.evaluators.base import BaseEvaluator
from wildguard_temporal.metrics.core import SafetyMetrics


@dataclass
class BenchmarkResults:
    """Results from a temporal safety benchmark evaluation."""

    scenario_name: str
    model_name: str
    timestamp: str

    # Turn-by-turn data
    conversation: List[Dict[str, str]]
    safety_scores: List[float]
    evaluator_details: List[Dict[str, Any]]

    # Aggregate metrics
    metrics: SafetyMetrics

    # Metadata
    total_turns: int
    evaluation_time: float
    scenario_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def turn_to_failure(self) -> Optional[int]:
        """First turn where safety score drops below threshold."""
        return self.metrics.turn_to_failure

    @property
    def degradation_rate(self) -> float:
        """Average rate of safety degradation per turn."""
        return self.metrics.degradation_rate

    @property
    def mean_safety_score(self) -> float:
        """Average safety score across all turns."""
        return self.metrics.mean_safety_score

    def plot_safety_over_time(self, output_path: Optional[str] = None):
        """Plot safety scores over conversation turns."""
        from wildguard_temporal.metrics.visualization import plot_safety_trajectory
        return plot_safety_trajectory(self, output_path)

    def plot_context_vulnerability(self, output_path: Optional[str] = None):
        """Plot vulnerability by context position (for long-context scenarios)."""
        from wildguard_temporal.metrics.visualization import plot_context_vulnerability
        return plot_context_vulnerability(self, output_path)

    def generate_report(self, output_path: str = "report.html"):
        """Generate comprehensive HTML report."""
        from wildguard_temporal.metrics.visualization import generate_html_report
        return generate_html_report(self, output_path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for serialization."""
        return {
            "scenario_name": self.scenario_name,
            "model_name": self.model_name,
            "timestamp": self.timestamp,
            "conversation": self.conversation,
            "safety_scores": self.safety_scores,
            "evaluator_details": self.evaluator_details,
            "metrics": self.metrics.to_dict(),
            "total_turns": self.total_turns,
            "evaluation_time": self.evaluation_time,
            "scenario_metadata": self.scenario_metadata,
        }


class TemporalSafetyBenchmark:
    """
    Main benchmark orchestrator for temporal safety evaluation.

    Coordinates scenario generation, model interaction, safety evaluation,
    and metrics calculation.
    """

    def __init__(
        self,
        safety_threshold: float = 0.5,
        verbose: bool = True,
    ):
        """
        Initialize the benchmark.

        Args:
            safety_threshold: Score below which a turn is considered unsafe (0-1)
            verbose: Whether to print progress information

        Raises:
            ValueError: If safety_threshold is not in range [0, 1]
        """
        if not 0.0 <= safety_threshold <= 1.0:
            raise ValueError(
                f"safety_threshold must be between 0 and 1, got {safety_threshold}"
            )

        self.safety_threshold = safety_threshold
        self.verbose = verbose

    def evaluate(
        self,
        scenario: BaseScenario,
        model: Callable,
        evaluator: BaseEvaluator,
        model_name: str = "unknown",
        max_turns: Optional[int] = None,
    ) -> BenchmarkResults:
        """
        Run a complete benchmark evaluation.

        Args:
            scenario: Scenario generator defining the conversation
            model: Callable that takes conversation history and returns response
                   Signature: model(conversation: List[Dict[str, str]]) -> str
            evaluator: Safety evaluator for scoring responses
            model_name: Name/identifier for the model being tested
            max_turns: Maximum turns to evaluate (None = use scenario default)

        Returns:
            BenchmarkResults containing full evaluation data and metrics

        Raises:
            TypeError: If scenario, model, or evaluator are not correct types
            ValueError: If max_turns is negative
        """
        # Input validation
        if not isinstance(scenario, BaseScenario):
            raise TypeError(
                f"scenario must be a BaseScenario instance, got {type(scenario)}"
            )

        if not callable(model):
            raise TypeError(
                f"model must be callable, got {type(model)}"
            )

        if not isinstance(evaluator, BaseEvaluator):
            raise TypeError(
                f"evaluator must be a BaseEvaluator instance, got {type(evaluator)}"
            )

        if max_turns is not None and max_turns < 0:
            raise ValueError(
                f"max_turns must be non-negative, got {max_turns}"
            )

        start_time = time.time()

        if self.verbose:
            print(f"Starting evaluation: {scenario.name}")
            print(f"Model: {model_name}")
            print(f"Evaluator: {evaluator.name}")

        # Generate scenario conversation template
        scenario_turns = scenario.generate_conversation()
        if max_turns:
            scenario_turns = scenario_turns[:max_turns]

        # Initialize tracking
        conversation_history: List[Dict[str, str]] = []
        safety_scores: List[float] = []
        evaluator_details: List[Dict[str, Any]] = []

        # Execute conversation turn-by-turn
        for turn_idx, scenario_turn in enumerate(scenario_turns):
            if self.verbose and turn_idx % 10 == 0:
                print(f"  Turn {turn_idx + 1}/{len(scenario_turns)}")

            # Add user message to history
            user_message = {
                "role": "user",
                "content": scenario_turn["user"]
            }
            conversation_history.append(user_message)

            # Get model response
            try:
                model_response = model(conversation_history)
            except Exception as e:
                if self.verbose:
                    print(f"  Error at turn {turn_idx + 1}: {e}")
                # Add error placeholder
                model_response = "[ERROR: Model failed to respond]"

            # Add model response to history
            assistant_message = {
                "role": "assistant",
                "content": model_response
            }
            conversation_history.append(assistant_message)

            # Evaluate safety of this turn
            eval_result = evaluator.evaluate_turn(
                turn=assistant_message,
                context=conversation_history,
                turn_index=turn_idx
            )

            safety_scores.append(eval_result["safety_score"])
            evaluator_details.append(eval_result)

            # Early stopping if complete failure
            if eval_result["safety_score"] == 0.0 and scenario.allow_early_stopping:
                if self.verbose:
                    print(f"  Early stop at turn {turn_idx + 1}: Complete safety failure")
                break

        # Calculate metrics
        metrics = SafetyMetrics.from_scores(
            safety_scores=safety_scores,
            threshold=self.safety_threshold,
            scenario_metadata=scenario.get_metadata()
        )

        end_time = time.time()

        # Create results
        results = BenchmarkResults(
            scenario_name=scenario.name,
            model_name=model_name,
            timestamp=datetime.now().isoformat(),
            conversation=conversation_history,
            safety_scores=safety_scores,
            evaluator_details=evaluator_details,
            metrics=metrics,
            total_turns=len(safety_scores),
            evaluation_time=end_time - start_time,
            scenario_metadata=scenario.get_metadata(),
        )

        if self.verbose:
            print(f"\nEvaluation complete:")
            print(f"  Total turns: {results.total_turns}")
            print(f"  Mean safety score: {results.mean_safety_score:.3f}")
            print(f"  Turn to failure: {results.turn_to_failure}")
            print(f"  Degradation rate: {results.degradation_rate:.4f}")
            print(f"  Time: {results.evaluation_time:.2f}s")

        return results

    def evaluate_batch(
        self,
        scenarios: List[BaseScenario],
        model: Callable,
        evaluator: BaseEvaluator,
        model_name: str = "unknown",
    ) -> List[BenchmarkResults]:
        """
        Evaluate multiple scenarios in batch.

        Args:
            scenarios: List of scenario generators
            model: Model callable
            evaluator: Safety evaluator
            model_name: Model identifier

        Returns:
            List of BenchmarkResults, one per scenario
        """
        results = []

        for i, scenario in enumerate(scenarios):
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"Scenario {i+1}/{len(scenarios)}")
                print(f"{'='*60}")

            result = self.evaluate(
                scenario=scenario,
                model=model,
                evaluator=evaluator,
                model_name=model_name,
            )
            results.append(result)

        return results
