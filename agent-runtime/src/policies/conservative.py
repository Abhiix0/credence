from typing import List, Optional, Tuple
from .base import BasePolicy
from ..models import Agent, Task, TaskStatus, Bid


class ConservativePolicy(BasePolicy):
    """
    Conservative bidding strategy:
    - Only bids if the agent strictly matches the required capability.
    - Demands 90-95% of the total posted reward.
    - Requests generous execution duration buffer.
    
    Scoring strategy (for buyer selection):
    - Heavily weights reputation (0.5)
    - Lower weight on price (0.15) and speed (0.1)
    - Applies risk-aversion penalty if reputation < 85
    """

    def __init__(self):
        super().__init__(name="ConservativePolicy")

    def evaluate(self, agent: Agent, task: Task) -> Tuple[bool, Optional[int], Optional[int]]:
        if task.status != TaskStatus.OPEN:
            return False, None, None

        # Check strict capability match
        if task.required_capability not in agent.capabilities:
            return False, None, None

        # Bid 95% of task reward to ensure profitability
        proposed_price = int(task.reward_wei * 0.95)
        # Safe 1800 second turnaround estimation
        estimated_duration = 1800

        return True, proposed_price, estimated_duration

    def score_bid(self, agent: Agent, task: Task, bid: Bid, all_bids: List[Bid]) -> float:
        """
        Conservative scoring: prioritize reputation and safety.
        
        Weights:
        - Reputation: 0.6 (increased to dominate)
        - Price efficiency: 0.1
        - Speed: 0.05
        - Capability match: 0.25
        - Strong risk penalty if reputation < 85
        """
        # Reputation component (0-100 scale, weight 0.6)
        reputation_score = agent.reputation.score
        reputation_component = (reputation_score / 100.0) * 60.0
        
        # Strong risk-aversion penalty for conservative buyers
        if reputation_score < 85:
            risk_penalty = (85 - reputation_score) * 0.8  # Much stronger penalty
            reputation_component -= risk_penalty
        
        # Price efficiency component (lower price = better, weight 0.1)
        if task.reward_wei > 0:
            price_efficiency = 1.0 - (bid.proposed_price_wei / task.reward_wei)
            price_component = max(0, price_efficiency) * 10.0
        else:
            price_component = 0.0
        
        # Speed component (faster = better, weight 0.05)
        # Normalize against all bids
        if all_bids and bid.estimated_duration_sec > 0:
            max_duration = max(b.estimated_duration_sec for b in all_bids if b.estimated_duration_sec > 0)
            if max_duration > 0:
                speed_efficiency = 1.0 - (bid.estimated_duration_sec / max_duration)
                speed_component = speed_efficiency * 5.0
            else:
                speed_component = 0.0
        else:
            speed_component = 0.0
        
        # Capability match component (weight 0.25)
        # Assume perfect match if agent has the required capability
        capability_component = 25.0 if task.required_capability in agent.capabilities else 0.0
        
        total_score = reputation_component + price_component + speed_component + capability_component
        return max(0.0, total_score)
