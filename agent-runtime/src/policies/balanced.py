from typing import List, Optional, Tuple
from .base import BasePolicy
from ..models import Agent, Task, TaskStatus, Bid


class BalancedPolicy(BasePolicy):
    """
    Balanced bidding strategy:
    - Middle ground between conservative and aggressive.
    - Bids around 80-85% of reward.
    - Moderate execution duration.
    
    Scoring strategy (for buyer selection):
    - Balanced weights across all factors
    - Reputation: 0.3
    - Price efficiency: 0.3
    - Speed: 0.2
    - Stake/Risk: 0.2
    """

    def __init__(self):
        super().__init__(name="BalancedPolicy")

    def evaluate(self, agent: Agent, task: Task) -> Tuple[bool, Optional[int], Optional[int]]:
        if task.status != TaskStatus.OPEN:
            return False, None, None

        # Check capability match
        if task.required_capability not in agent.capabilities:
            return False, None, None

        # Bid 85% of task reward - middle ground
        proposed_price = int(task.reward_wei * 0.85)
        # Moderate turnaround: 1200 seconds
        estimated_duration = 1200

        return True, proposed_price, estimated_duration

    def score_bid(self, agent: Agent, task: Task, bid: Bid, all_bids: List[Bid]) -> float:
        """
        Balanced scoring: even consideration of all factors with emphasis on trustworthiness.
        
        Weights:
        - Reputation: 0.4 (reliable workers valued)
        - Price efficiency: 0.22
        - Speed: 0.18
        - Risk penalty: 0.2 (strong penalty for low reputation)
        """
        # Reputation component (0-100 scale, weight 0.4)
        reputation_score = agent.reputation.score
        reputation_component = (reputation_score / 100.0) * 40.0
        
        # Price efficiency component (lower price = better, weight 0.22)
        if task.reward_wei > 0:
            price_efficiency = 1.0 - (bid.proposed_price_wei / task.reward_wei)
            price_component = max(0, price_efficiency) * 22.0
        else:
            price_component = 0.0
        
        # Speed component (faster = better, weight 0.18)
        if all_bids and bid.estimated_duration_sec > 0:
            max_duration = max(b.estimated_duration_sec for b in all_bids if b.estimated_duration_sec > 0)
            if max_duration > 0:
                speed_efficiency = 1.0 - (bid.estimated_duration_sec / max_duration)
                speed_component = speed_efficiency * 18.0
            else:
                speed_component = 0.0
        else:
            speed_component = 0.0
        
        # Risk/Stake component (weight 0.2)
        # Future: will incorporate stake_wei once Vault exists
        # Strong penalty for low reputation to balance price-chasing
        risk_component = 10.0  # Base value (half of max 20)
        if reputation_score < 80:
            # Stronger penalty for low reputation (doubled from 0.15 to 0.25)
            risk_component -= (80 - reputation_score) * 0.25
        elif reputation_score > 90:
            risk_component += (reputation_score - 90) * 0.2
        
        risk_component = max(0, min(20.0, risk_component))
        
        total_score = reputation_component + price_component + speed_component + risk_component
        return max(0.0, total_score)
