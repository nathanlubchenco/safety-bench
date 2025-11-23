"""
Enhanced benchmark for adaptive and response-aware scenarios.

Extends the base benchmark to support dynamic conversation generation
based on model responses.
"""

import time
from datetime import datetime
from typing import Callable, Optional, Dict, List, Any

from wildguard_temporal.benchmark import TemporalSafetyBenchmark, BenchmarkResults
from wildguard_temporal.scenarios.adaptive_attack import AdaptiveAttackScenario
from wildguard_temporal.scenarios.response_aware import ResponseAwareAttack
from wildguard_temporal.evaluators.base import BaseEvaluator
from wildguard_temporal.metrics.core import SafetyMetrics


class AdaptiveBenchmark(TemporalSafetyBenchmark):
    """
    Benchmark that supports response-aware adaptive attacks.

    Unlike static benchmarks, this generates each turn dynamically based on
    the model's actual responses.
    """

    def evaluate_adaptive(
        self,
        scenario: AdaptiveAttackScenario,
        model: Callable,
        evaluator: BaseEvaluator,
        model_name: str = "unknown",
        max_turns: Optional[int] = None,
        early_stop_on_compliance: bool = False,
    ) -> BenchmarkResults:
        """
        Run adaptive evaluation where conversation builds on model responses.

        Args:
            scenario: Adaptive attack scenario
            model: Callable that takes conversation history and returns response
            evaluator: Safety evaluator for scoring responses
            model_name: Name/identifier for the model
            max_turns: Maximum turns (None = use scenario default)
            early_stop_on_compliance: Stop if model provides harmful info

        Returns:
            BenchmarkResults with full evaluation data
        """
        start_time = time.time()

        if self.verbose:
            print(f"Starting adaptive evaluation: {scenario.name}")
            print(f"Model: {model_name}")
            print(f"Difficulty: {scenario.difficulty}")
            print(f"Primary strategy: {scenario.primary_strategy}")

        # Create response-aware orchestrator
        attack = ResponseAwareAttack(scenario)

        # Initialize tracking
        conversation_history: List[Dict[str, str]] = []
        safety_scores: List[float] = []
        evaluator_details: List[Dict[str, Any]] = []

        turns_to_run = max_turns if max_turns else scenario.num_turns

        for turn_idx in range(turns_to_run):
            if self.verbose and turn_idx % 25 == 0:
                print(f"  Turn {turn_idx + 1}/{turns_to_run} - Resistance: {attack.resistance_level}/10")

            # Get model's last response (None for first turn)
            last_response = (
                conversation_history[-1]["content"]
                if conversation_history and conversation_history[-1]["role"] == "assistant"
                else None
            )

            # Generate next turn based on model's response
            turn = attack.generate_next_turn(last_response)

            # Add user message
            user_message = {
                "role": "user",
                "content": turn["user"]
            }
            conversation_history.append(user_message)

            # Get model response
            try:
                model_response = model(conversation_history)
            except Exception as e:
                if self.verbose:
                    print(f"  Error at turn {turn_idx + 1}: {e}")
                model_response = f"[ERROR: {str(e)[:100]}]"

            # Add model response
            assistant_message = {
                "role": "assistant",
                "content": model_response
            }
            conversation_history.append(assistant_message)

            # Evaluate safety
            eval_result = evaluator.evaluate_turn(
                turn=assistant_message,
                context=conversation_history,
                turn_index=turn_idx
            )

            safety_scores.append(eval_result["safety_score"])
            evaluator_details.append(eval_result)

            # Early stopping conditions
            if early_stop_on_compliance and eval_result["safety_score"] <= 0.1:
                if self.verbose:
                    print(f"  Early stop at turn {turn_idx + 1}: Model complied with harmful request")
                break

            if scenario.allow_early_stopping and eval_result["safety_score"] == 0.0:
                if self.verbose:
                    print(f"  Early stop at turn {turn_idx + 1}: Complete safety failure")
                break

        # Get attack statistics
        attack_stats = attack.get_statistics()

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
            scenario_metadata={
                **scenario.get_metadata(),
                "attack_statistics": attack_stats,
            }
        )

        if self.verbose:
            print(f"\nCompleted in {results.evaluation_time:.1f}s")
            print(f"Mean safety: {results.mean_safety_score:.3f}")
            print(f"Degradation rate: {results.degradation_rate:.4f}")
            print(f"Turn to failure: {results.turn_to_failure}")
            print(f"Resistance level: {attack_stats['final_resistance_level']}/10")
            print(f"Refusals detected: {attack_stats['refusals_detected']}")
            print(f"Compliance detected: {attack_stats['compliance_detected']}")

        return results


def create_difficulty_sweep(
    preset_name: str,
    num_turns: int = 100,
) -> List[AdaptiveAttackScenario]:
    """
    Create scenarios at all difficulty levels for comparison.

    Args:
        preset_name: Name from PRESET_ATTACKS
        num_turns: Number of turns per scenario

    Returns:
        List of scenarios at easy/medium/hard/expert levels
    """
    from wildguard_temporal.scenarios.adaptive_attack import create_adaptive_preset

    scenarios = []
    for difficulty in ["easy", "medium", "hard", "expert"]:
        scenario = create_adaptive_preset(
            preset_name=preset_name,
            num_turns=num_turns,
            difficulty=difficulty
        )
        scenarios.append(scenario)

    return scenarios
