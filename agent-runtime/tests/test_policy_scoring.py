"""
Test policy scoring against PRD's worked example.

PRD Example:
- Task reward: 0.05 ETH (50000000000000000 wei)
- Worker A: reputation 98, bid 0.045 ETH (90% of reward)
- Worker B: reputation 72, bid 0.025 ETH (50% of reward)
- Worker C: reputation 91, bid 0.035 ETH (70% of reward)

Expected outcomes:
- Conservative → selects Worker A (highest reputation)
- Aggressive → selects Worker B (lowest price)
- Balanced → selects Worker C (best overall balance)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

from src.models import Agent, Task, Bid, Reputation, TaskStatus
from src.policies import ConservativePolicy, AggressivePolicy, BalancedPolicy


def test_prd_worked_example():
    """Test that policy scoring matches PRD's worked example exactly."""
    
    # Setup task
    task = Task(
        task_id=1,
        creator="0xBuyer123",
        specification_uri="ipfs://task-spec",
        required_capability="coding",
        reward_wei=50000000000000000,  # 0.05 ETH
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    
    # Worker A: High reputation (98), high price (90% = 0.045 ETH)
    agent_a = Agent(
        wallet_address="0xWorkerA",
        name="WorkerA",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerA", score=98),
        policy_name="ConservativePolicy",
    )
    bid_a = Bid(
        bid_id=1,
        task_id=1,
        bidder="0xWorkerA",
        proposed_price_wei=45000000000000000,  # 0.045 ETH (90%)
        estimated_duration_sec=1200,
        timestamp=1000000,
    )
    
    # Worker B: Low reputation (72), low price (50% = 0.025 ETH)
    agent_b = Agent(
        wallet_address="0xWorkerB",
        name="WorkerB",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerB", score=72),
        policy_name="AggressivePolicy",
    )
    bid_b = Bid(
        bid_id=2,
        task_id=1,
        bidder="0xWorkerB",
        proposed_price_wei=25000000000000000,  # 0.025 ETH (50%)
        estimated_duration_sec=600,
        timestamp=1000001,
    )
    
    # Worker C: Good reputation (91), moderate price (70% = 0.035 ETH)
    agent_c = Agent(
        wallet_address="0xWorkerC",
        name="WorkerC",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerC", score=91),
        policy_name="BalancedPolicy",
    )
    bid_c = Bid(
        bid_id=3,
        task_id=1,
        bidder="0xWorkerC",
        proposed_price_wei=35000000000000000,  # 0.035 ETH (70%)
        estimated_duration_sec=900,
        timestamp=1000002,
    )
    
    all_bids = [bid_a, bid_b, bid_c]
    
    # Test Conservative Policy - should select Worker A (highest reputation)
    conservative = ConservativePolicy()
    score_a_conservative = conservative.score_bid(agent_a, task, bid_a, all_bids)
    score_b_conservative = conservative.score_bid(agent_b, task, bid_b, all_bids)
    score_c_conservative = conservative.score_bid(agent_c, task, bid_c, all_bids)
    
    print(f"\nConservative Policy Scores:")
    print(f"  Worker A (rep 98, bid 90%): {score_a_conservative:.2f}")
    print(f"  Worker B (rep 72, bid 50%): {score_b_conservative:.2f}")
    print(f"  Worker C (rep 91, bid 70%): {score_c_conservative:.2f}")
    
    assert score_a_conservative > score_b_conservative, \
        f"Conservative should prefer A over B (A={score_a_conservative:.2f}, B={score_b_conservative:.2f})"
    assert score_a_conservative > score_c_conservative, \
        f"Conservative should prefer A over C (A={score_a_conservative:.2f}, C={score_c_conservative:.2f})"
    
    # Test Aggressive Policy - should select Worker B (lowest price)
    aggressive = AggressivePolicy()
    score_a_aggressive = aggressive.score_bid(agent_a, task, bid_a, all_bids)
    score_b_aggressive = aggressive.score_bid(agent_b, task, bid_b, all_bids)
    score_c_aggressive = aggressive.score_bid(agent_c, task, bid_c, all_bids)
    
    print(f"\nAggressive Policy Scores:")
    print(f"  Worker A (rep 98, bid 90%): {score_a_aggressive:.2f}")
    print(f"  Worker B (rep 72, bid 50%): {score_b_aggressive:.2f}")
    print(f"  Worker C (rep 91, bid 70%): {score_c_aggressive:.2f}")
    
    assert score_b_aggressive > score_a_aggressive, \
        f"Aggressive should prefer B over A (B={score_b_aggressive:.2f}, A={score_a_aggressive:.2f})"
    assert score_b_aggressive > score_c_aggressive, \
        f"Aggressive should prefer B over C (B={score_b_aggressive:.2f}, C={score_c_aggressive:.2f})"
    
    # Test Balanced Policy - should select Worker C (best balance)
    balanced = BalancedPolicy()
    score_a_balanced = balanced.score_bid(agent_a, task, bid_a, all_bids)
    score_b_balanced = balanced.score_bid(agent_b, task, bid_b, all_bids)
    score_c_balanced = balanced.score_bid(agent_c, task, bid_c, all_bids)
    
    print(f"\nBalanced Policy Scores:")
    print(f"  Worker A (rep 98, bid 90%): {score_a_balanced:.2f}")
    print(f"  Worker B (rep 72, bid 50%): {score_b_balanced:.2f}")
    print(f"  Worker C (rep 91, bid 70%): {score_c_balanced:.2f}")
    
    assert score_c_balanced > score_a_balanced, \
        f"Balanced should prefer C over A (C={score_c_balanced:.2f}, A={score_a_balanced:.2f})"
    assert score_c_balanced > score_b_balanced, \
        f"Balanced should prefer C over B (C={score_c_balanced:.2f}, B={score_b_balanced:.2f})"
    
    print("\n✅ All PRD worked example assertions passed!")


def test_score_bid_returns_non_negative():
    """Ensure all policies return non-negative scores."""
    
    task = Task(
        task_id=1,
        creator="0xBuyer",
        specification_uri="ipfs://spec",
        required_capability="testing",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    
    agent = Agent(
        wallet_address="0xWorker",
        name="Worker",
        capabilities=["testing"],
        reputation=Reputation(agent_address="0xWorker", score=85),
        policy_name="ConservativePolicy",
    )
    
    bid = Bid(
        bid_id=1,
        task_id=1,
        bidder="0xWorker",
        proposed_price_wei=800000000000000000,
        estimated_duration_sec=1200,
        timestamp=1000000,
    )
    
    policies = [ConservativePolicy(), AggressivePolicy(), BalancedPolicy()]
    
    for policy in policies:
        score = policy.score_bid(agent, task, bid, [bid])
        assert score >= 0, f"{policy.name} returned negative score: {score}"
        print(f"{policy.name} score: {score:.2f}")


if __name__ == "__main__":
    test_prd_worked_example()
    test_score_bid_returns_non_negative()
    print("\n✅ All tests passed!")
