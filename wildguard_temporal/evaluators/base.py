"""
Base evaluator interface for safety assessment.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseEvaluator(ABC):
    """
    Base class for safety evaluators.

    Evaluators score model responses for safety on a scale from 0.0 (unsafe)
    to 1.0 (safe).
    """

    def __init__(self, name: str = "BaseEvaluator"):
        """
        Initialize evaluator.

        Args:
            name: Evaluator identifier
        """
        self.name = name

    @abstractmethod
    def evaluate_turn(
        self,
        turn: Dict[str, str],
        context: List[Dict[str, str]],
        turn_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Evaluate safety of a conversation turn.

        Args:
            turn: Current turn with 'role' and 'content'
            context: Full conversation history up to this point
            turn_index: Index of this turn (0-based)

        Returns:
            Dictionary with:
                - 'safety_score': float from 0.0 (unsafe) to 1.0 (safe)
                - 'reasoning': str explaining the score (optional)
                - 'violations': list of detected safety violations (optional)
                - Additional evaluator-specific fields
        """
        pass

    def batch_evaluate(
        self,
        turns: List[Dict[str, str]],
        contexts: List[List[Dict[str, str]]],
    ) -> List[Dict[str, Any]]:
        """
        Evaluate multiple turns in batch (override for efficiency).

        Args:
            turns: List of conversation turns
            contexts: List of conversation contexts for each turn

        Returns:
            List of evaluation results
        """
        results = []
        for i, (turn, context) in enumerate(zip(turns, contexts)):
            result = self.evaluate_turn(turn, context, turn_index=i)
            results.append(result)
        return results

    def get_config(self) -> Dict[str, Any]:
        """
        Get evaluator configuration for reproducibility.

        Returns:
            Dictionary of evaluator settings
        """
        return {
            "name": self.name,
            "class": self.__class__.__name__,
        }
