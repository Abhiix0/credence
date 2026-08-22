from abc import ABC, abstractmethod
from typing import Optional, Tuple
from ..models import Agent, Task


class BasePolicy(ABC):
    """Abstract policy interface defining how agents evaluate and price tasks."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def evaluate(self, agent: Agent, task: Task) -> Tuple[bool, Optional[int], Optional[int]]:
        """
        Evaluate a discovered task.
        
        Returns:
            Tuple[should_bid: bool, proposed_price_wei: Optional[int], estimated_duration_sec: Optional[int]]
        """
        pass
