"""
Response inspector-based evaluator - more sophisticated than keyword matching.
"""

from typing import Any, Dict, List
from wildguard_temporal.evaluators.base import BaseEvaluator
from wildguard_temporal.utils.response_inspector import ResponseInspector


class InspectorBasedEvaluator(BaseEvaluator):
    """
    Evaluator using response inspection to distinguish refusals from compliance.

    This is more sophisticated than simple keyword matching because it:
    - Distinguishes safe refusals from unsafe compliance
    - Detects hedging and mixed signals
    - Provides behavior classification
    - Gives more accurate safety scores
    """

    def __init__(self, name: str = "InspectorBasedEvaluator"):
        """
        Initialize inspector-based evaluator.

        Args:
            name: Evaluator identifier
        """
        super().__init__(name=name)
        self.inspector = ResponseInspector()

    def evaluate_turn(
        self,
        turn: Dict[str, str],
        context: List[Dict[str, str]],
        turn_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Evaluate turn using response inspection.

        Args:
            turn: Current turn
            context: Conversation history
            turn_index: Turn index

        Returns:
            Evaluation result with safety score and behavior classification
        """
        content = turn.get("content", "")

        # Inspect response
        inspection = self.inspector.inspect_response(content)

        return {
            "safety_score": inspection["safety_score"],
            "behavior_type": inspection["behavior_type"],
            "explanation": inspection["explanation"],
            "strong_refusals": len(inspection["strong_refusals"]),
            "compliance_indicators": len(inspection["compliance_indicators"]),
            "hedges": len(inspection["hedges"]),
            "response_length": inspection["response_length"],
            "evaluator": self.name,
            "reasoning": self._generate_reasoning(inspection),
        }

    def _generate_reasoning(self, inspection: Dict[str, Any]) -> str:
        """Generate explanation for the evaluation."""
        behavior = inspection["behavior_type"]
        score = inspection["safety_score"]

        parts = [f"Behavior: {behavior} (score: {score:.2f})"]

        if inspection["strong_refusals"]:
            parts.append(f"{len(inspection['strong_refusals'])} refusal patterns")

        if inspection["compliance_indicators"]:
            parts.append(f"{len(inspection['compliance_indicators'])} compliance indicators")

        if inspection["hedges"]:
            parts.append(f"{len(inspection['hedges'])} hedging patterns")

        return " | ".join(parts)

    def get_config(self) -> Dict[str, Any]:
        """Get evaluator configuration."""
        config = super().get_config()
        config.update({
            "uses_response_inspection": True,
            "distinguishes_refusals": True,
        })
        return config
