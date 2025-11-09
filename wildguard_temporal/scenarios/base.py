"""
Base scenario class for temporal safety testing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ConversationTurn:
    """Represents a single conversation turn."""
    user: str
    expected_safety_level: float  # 0.0 (unsafe) to 1.0 (safe)
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseScenario(ABC):
    """
    Base class for temporal safety scenarios.

    Scenarios generate conversation templates that test specific aspects
    of temporal safety degradation.
    """

    def __init__(
        self,
        name: str,
        description: str,
        num_turns: int,
        allow_early_stopping: bool = False,
    ):
        """
        Initialize base scenario.

        Args:
            name: Scenario identifier
            description: Human-readable description
            num_turns: Number of conversation turns to generate
            allow_early_stopping: Whether to stop early on complete failure
        """
        self.name = name
        self.description = description
        self.num_turns = num_turns
        self.allow_early_stopping = allow_early_stopping

    @abstractmethod
    def generate_conversation(self) -> List[Dict[str, str]]:
        """
        Generate the conversation template for this scenario.

        Returns:
            List of conversation turns, each with:
                - 'user': User message content
                - 'expected_safety': Expected safety level (0-1)
                - 'metadata': Optional turn-specific metadata
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get scenario metadata for analysis.

        Returns:
            Dictionary with scenario configuration and properties
        """
        return {
            "name": self.name,
            "description": self.description,
            "num_turns": self.num_turns,
            "scenario_type": self.__class__.__name__,
        }

    def get_ground_truth_labels(self) -> List[float]:
        """
        Get expected safety labels for each turn.

        Returns:
            List of expected safety scores (0-1) per turn
        """
        conversation = self.generate_conversation()
        return [turn.get("expected_safety", 1.0) for turn in conversation]
