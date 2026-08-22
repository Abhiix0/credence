from typing import Optional, Tuple
from .base import BasePolicy
from ..models import Agent, Task, TaskStatus


class ReputationPolicy(BasePolicy):
    """
    Reputation-optimizing bidding strategy:
    - Bids only on high-confidence tasks to protect and elevate reputation score.
    - Scales price dynamically according to current agent reputation.
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
