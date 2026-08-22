from typing import List, Optional, Tuple
from .base import BasePolicy
from ..models import Agent, Task, TaskStatus, Bid


class AggressivePolicy(BasePolicy):
    """
    Aggressive bidding strategy:
    - Bids aggressively to undercut competitors (e.g. 70-80% of reward).
    - Accepts broader capability overlaps.
    - Promises faster execution duration.
    
    Scoring strategy (for buyer selection):
    - Heavily weights price (0.5) - cheapest wins
    - High weight on speed (0.25)
    - Lower weight on reputation (0.15)
    - No risk penalty
    """

    def __init__(self):
        super().__init__(name="AggressivePolicy")

    def evaluate(self, agent: Agent, task: Task) -> Tuple[bool, Optional[int], Optional[int]]:
        if task.status != TaskStatus.OPEN:
            return False, None, None

        # Undercut market at 75% of maximum task reward
        proposed_price = max(int(task.reward_wei * 0.75), 1)
        # Fast turnaround: 600 seconds
        estimated_duration = 600

        return True, proposed_price, estimated_duration

    def score_bid(self, agent: Agent, task: Task, bid: Bid, all_bids: List[Bid]) -> float:
        """
        Aggressive scoring: prioritize low price and fast delivery.
        
        Weights:
        - Price efficiency: 0.5 (most important)
        - Speed: 0.25
        - Reputation: 0.15
        - Capability match: 0.1
        - No risk penalty
        """
        # Price efficiency component (lower price = better, weight 0.5)
        if task.reward_wei > 0:
            price_efficiency = 1.0 - (bid.proposed_price_wei / task.reward_wei)
            price_component = max(0, price_efficiency) * 50.0
        else:
            price_component = 0.0
        
        # Speed component (faster = better, weight 0.25)
        if all_bids and bid.estimated_duration_sec > 0:
            max_duration = max(b.estimated_duration_sec for b in all_bids if b.estimated_duration_sec > 0)
            if max_duration > 0:
                speed_efficiency = 1.0 - (bid.estimated_duration_sec / max_duration)
                speed_component = speed_efficiency * 25.0
            else:
                speed_component = 0.0
        else:
            speed_component = 0.0
        
        # Reputation component (0-100 scale, weight 0.15)
        reputation_score = agent.reputation.score
        reputation_component = (reputation_score / 100.0) * 15.0
        
        # Capability match component (weight 0.1)
        capability_component = 10.0 if task.required_capability in agent.capabilities else 0.0
        
        total_score = price_component + speed_component + reputation_component + capability_component
        return max(0.0, total_score)
