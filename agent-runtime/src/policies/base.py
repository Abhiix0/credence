from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from ..models import Agent, Task, Bid


class BasePolicy(ABC):
    """Abstract policy interface defining how agents evaluate and price tasks."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def evaluate(self, agent: Agent, task: Task) -> Tuple[bool, Optional[int], Optional[int]]:
        """
        Evaluate a discovered task for bidding.
        
        Returns:
            Tuple[should_bid: bool, proposed_price_wei: Optional[int], estimated_duration_sec: Optional[int]]
        """
        pass

    @abstractmethod
    def score_bid(self, agent: Agent, task: Task, bid: Bid, all_bids: List[Bid]) -> float:
        """
        Score a competing bid for buyer's worker selection.
        
        Args:
            agent: The bidder's Agent object (with reputation data)
            task: The task being bid on
            bid: The specific bid to score
            all_bids: All bids for this task (for normalization)
        
        Returns:
            Score (higher is better), typically in range [0, 100]
        """
        pass
