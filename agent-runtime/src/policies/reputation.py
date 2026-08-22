from typing import List, Optional, Tuple
from .base import BasePolicy
from ..models import Agent, Task, TaskStatus, Bid


class ReputationPolicy(BasePolicy):
    """
    Reputation-optimizing bidding strategy:
    - Bids only on high-confidence tasks to protect and elevate reputation score.
    - Scales price dynamically according to current agent reputation.
    
    Scoring strategy (for buyer selection):
    - Very high weight on reputation (0.6) - reputation is paramount
    - Moderate weight on price (0.2)
    - Lower weight on speed (0.1)
    - Capability match (0.1)
    """

    def __init__(self):
        super().__init__(name="ReputationPolicy")

    def evaluate(self, agent: Agent, task: Task) -> Tuple[bool, Optional[int], Optional[int]]:
        if task.status != TaskStatus.OPEN:
            return False, None, None

        # Requires capability match and positive reputation
        if task.required_capability not in agent.capabilities:
            return False, None, None

        if agent.reputation.score < 50:
            # Low reputation: bid discounted to rebuild trust
            proposed_price = int(task.reward_wei * 0.80)
        else:
            # Established reputation: bid premium
            proposed_price = int(task.reward_wei * 0.90)

        estimated_duration = 1200
        return True, proposed_price, estimated_duration

    def score_bid(self, agent: Agent, task: Task, bid: Bid, all_bids: List[Bid]) -> float:
        """
        Reputation-focused scoring: reputation dominates selection.
        
        Weights:
        - Reputation: 0.6 (dominant factor)
        - Price efficiency: 0.2
        - Speed: 0.1
        - Capability match: 0.1
        """
        # Reputation component (0-100 scale, weight 0.6)
        reputation_score = agent.reputation.score
        reputation_component = (reputation_score / 100.0) * 60.0
        
        # Price efficiency component (lower price = better, weight 0.2)
        if task.reward_wei > 0:
            price_efficiency = 1.0 - (bid.proposed_price_wei / task.reward_wei)
            price_component = max(0, price_efficiency) * 20.0
        else:
            price_component = 0.0
        
        # Speed component (faster = better, weight 0.1)
        if all_bids and bid.estimated_duration_sec > 0:
            max_duration = max(b.estimated_duration_sec for b in all_bids if b.estimated_duration_sec > 0)
            if max_duration > 0:
                speed_efficiency = 1.0 - (bid.estimated_duration_sec / max_duration)
                speed_component = speed_efficiency * 10.0
            else:
                speed_component = 0.0
        else:
            speed_component = 0.0
        
        # Capability match component (weight 0.1)
        capability_component = 10.0 if task.required_capability in agent.capabilities else 0.0
        
        total_score = reputation_component + price_component + speed_component + capability_component
        return max(0.0, total_score)
