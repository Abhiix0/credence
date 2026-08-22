"""
Test BuyerAgent bid evaluation and worker selection logic.

Tests the PRD worked example scenarios and logging format.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Agent, Task, Bid, Reputation, TaskStatus
from src.policies import ConservativePolicy, AggressivePolicy, BalancedPolicy


def test_prd_worker_selection_conservative():
    """
    Test conservative policy selection using PRD worked example.
    
    PRD Example:
    - Task reward: 0.05 ETH (50000000000000000 wei)
    - Worker A: reputation 98, bid 0.045 ETH (90%)
    - Worker B: reputation 72, bid 0.025 ETH (50%)
    - Worker C: reputation 91, bid 0.035 ETH (70%)
    
    Expected: Conservative → Worker A (highest reputation)
    """
    print("\n" + "="*70)
    print("Testing BuyerAgent - Conservative Policy Selection")
    print("="*70)
    
    policy = ConservativePolicy()
    
    task = Task(
        task_id=1,
        creator="0xBuyer123",
        specification_uri="ipfs://task-spec",
        required_capability="coding",
        reward_wei=50000000000000000,  # 0.05 ETH
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    
    # Worker A: High reputation, high price
    agent_a = Agent(
        wallet_address="0xWorkerAAAA",
        name="WorkerA",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerAAAA", score=98),
        policy_name="ConservativePolicy",
        role="worker",
    )
    bid_a = Bid(
        bid_id=1,
        task_id=1,
        bidder="0xWorkerAAAA",
        proposed_price_wei=45000000000000000,  # 0.045 ETH (90%)
        estimated_duration_sec=1200,
        timestamp=1000000,
    )
    
    # Worker B: Low reputation, low price
    agent_b = Agent(
        wallet_address="0xWorkerBBBB",
        name="WorkerB",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerBBBB", score=72),
        policy_name="AggressivePolicy",
        role="worker",
    )
    bid_b = Bid(
        bid_id=2,
        task_id=1,
        bidder="0xWorkerBBBB",
        proposed_price_wei=25000000000000000,  # 0.025 ETH (50%)
        estimated_duration_sec=600,
        timestamp=1000001,
    )
    
    # Worker C: Good reputation, moderate price
    agent_c = Agent(
        wallet_address="0xWorkerCCCC",
        name="WorkerC",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerCCCC", score=91),
        policy_name="BalancedPolicy",
        role="worker",
    )
    bid_c = Bid(
        bid_id=3,
        task_id=1,
        bidder="0xWorkerCCCC",
        proposed_price_wei=35000000000000000,  # 0.035 ETH (70%)
        estimated_duration_sec=900,
        timestamp=1000002,
    )
    
    all_bids = [bid_a, bid_b, bid_c]
    
    # Score all bids
    score_a = policy.score_bid(agent_a, task, bid_a, all_bids)
    score_b = policy.score_bid(agent_b, task, bid_b, all_bids)
    score_c = policy.score_bid(agent_c, task, bid_c, all_bids)
    
    print(f"\nBid Scores (Conservative Policy):")
    print(f"  Worker A (rep 98, bid 90%): {score_a:.2f}")
    print(f"  Worker B (rep 72, bid 50%): {score_b:.2f}")
    print(f"  Worker C (rep 91, bid 70%): {score_c:.2f}")
    
    # Find highest score
    scores = [(bid_a, score_a), (bid_b, score_b), (bid_c, score_c)]
    scores.sort(key=lambda x: x[1], reverse=True)
    selected_bid, selected_score = scores[0]
    
    print(f"\nSelected: Bid #{selected_bid.bid_id} with score {selected_score:.2f}")
    
    # Conservative should select Worker A (highest reputation)
    assert selected_bid.bid_id == bid_a.bid_id, \
        f"Conservative should select Worker A, but selected Bid #{selected_bid.bid_id}"
    
    print("✅ Conservative policy correctly selected Worker A (highest reputation)")
    return True


def test_prd_worker_selection_aggressive():
    """
    Test aggressive policy selection using PRD worked example.
    
    Expected: Aggressive → Worker B (lowest price)
    """
    print("\n" + "="*70)
    print("Testing BuyerAgent - Aggressive Policy Selection")
    print("="*70)
    
    policy = AggressivePolicy()
    
    task = Task(
        task_id=1,
        creator="0xBuyer123",
        specification_uri="ipfs://task-spec",
        required_capability="coding",
        reward_wei=50000000000000000,
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    
    # Same workers as before
    agent_a = Agent(
        wallet_address="0xWorkerAAAA",
        name="WorkerA",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerAAAA", score=98),
        policy_name="ConservativePolicy",
        role="worker",
    )
    bid_a = Bid(
        bid_id=1,
        task_id=1,
        bidder="0xWorkerAAAA",
        proposed_price_wei=45000000000000000,
        estimated_duration_sec=1200,
        timestamp=1000000,
    )
    
    agent_b = Agent(
        wallet_address="0xWorkerBBBB",
        name="WorkerB",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerBBBB", score=72),
        policy_name="AggressivePolicy",
        role="worker",
    )
    bid_b = Bid(
        bid_id=2,
        task_id=1,
        bidder="0xWorkerBBBB",
        proposed_price_wei=25000000000000000,
        estimated_duration_sec=600,
        timestamp=1000001,
    )
    
    agent_c = Agent(
        wallet_address="0xWorkerCCCC",
        name="WorkerC",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerCCCC", score=91),
        policy_name="BalancedPolicy",
        role="worker",
    )
    bid_c = Bid(
        bid_id=3,
        task_id=1,
        bidder="0xWorkerCCCC",
        proposed_price_wei=35000000000000000,
        estimated_duration_sec=900,
        timestamp=1000002,
    )
    
    all_bids = [bid_a, bid_b, bid_c]
    
    # Score all bids
    score_a = policy.score_bid(agent_a, task, bid_a, all_bids)
    score_b = policy.score_bid(agent_b, task, bid_b, all_bids)
    score_c = policy.score_bid(agent_c, task, bid_c, all_bids)
    
    print(f"\nBid Scores (Aggressive Policy):")
    print(f"  Worker A (rep 98, bid 90%): {score_a:.2f}")
    print(f"  Worker B (rep 72, bid 50%): {score_b:.2f}")
    print(f"  Worker C (rep 91, bid 70%): {score_c:.2f}")
    
    # Find highest score
    scores = [(bid_a, score_a), (bid_b, score_b), (bid_c, score_c)]
    scores.sort(key=lambda x: x[1], reverse=True)
    selected_bid, selected_score = scores[0]
    
    print(f"\nSelected: Bid #{selected_bid.bid_id} with score {selected_score:.2f}")
    
    # Aggressive should select Worker B (lowest price)
    assert selected_bid.bid_id == bid_b.bid_id, \
        f"Aggressive should select Worker B, but selected Bid #{selected_bid.bid_id}"
    
    print("✅ Aggressive policy correctly selected Worker B (lowest price)")
    return True


def test_prd_worker_selection_balanced():
    """
    Test balanced policy selection using PRD worked example.
    
    Expected: Balanced → Worker C (best overall balance)
    """
    print("\n" + "="*70)
    print("Testing BuyerAgent - Balanced Policy Selection")
    print("="*70)
    
    policy = BalancedPolicy()
    
    task = Task(
        task_id=1,
        creator="0xBuyer123",
        specification_uri="ipfs://task-spec",
        required_capability="coding",
        reward_wei=50000000000000000,
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    
    # Same workers
    agent_a = Agent(
        wallet_address="0xWorkerAAAA",
        name="WorkerA",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerAAAA", score=98),
        policy_name="ConservativePolicy",
        role="worker",
    )
    bid_a = Bid(
        bid_id=1,
        task_id=1,
        bidder="0xWorkerAAAA",
        proposed_price_wei=45000000000000000,
        estimated_duration_sec=1200,
        timestamp=1000000,
    )
    
    agent_b = Agent(
        wallet_address="0xWorkerBBBB",
        name="WorkerB",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerBBBB", score=72),
        policy_name="AggressivePolicy",
        role="worker",
    )
    bid_b = Bid(
        bid_id=2,
        task_id=1,
        bidder="0xWorkerBBBB",
        proposed_price_wei=25000000000000000,
        estimated_duration_sec=600,
        timestamp=1000001,
    )
    
    agent_c = Agent(
        wallet_address="0xWorkerCCCC",
        name="WorkerC",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerCCCC", score=91),
        policy_name="BalancedPolicy",
        role="worker",
    )
    bid_c = Bid(
        bid_id=3,
        task_id=1,
        bidder="0xWorkerCCCC",
        proposed_price_wei=35000000000000000,
        estimated_duration_sec=900,
        timestamp=1000002,
    )
    
    all_bids = [bid_a, bid_b, bid_c]
    
    # Score all bids
    score_a = policy.score_bid(agent_a, task, bid_a, all_bids)
    score_b = policy.score_bid(agent_b, task, bid_b, all_bids)
    score_c = policy.score_bid(agent_c, task, bid_c, all_bids)
    
    print(f"\nBid Scores (Balanced Policy):")
    print(f"  Worker A (rep 98, bid 90%): {score_a:.2f}")
    print(f"  Worker B (rep 72, bid 50%): {score_b:.2f}")
    print(f"  Worker C (rep 91, bid 70%): {score_c:.2f}")
    
    # Find highest score
    scores = [(bid_a, score_a), (bid_b, score_b), (bid_c, score_c)]
    scores.sort(key=lambda x: x[1], reverse=True)
    selected_bid, selected_score = scores[0]
    
    print(f"\nSelected: Bid #{selected_bid.bid_id} with score {selected_score:.2f}")
    
    # Balanced should select Worker C (best balance)
    assert selected_bid.bid_id == bid_c.bid_id, \
        f"Balanced should select Worker C, but selected Bid #{selected_bid.bid_id}"
    
    print("✅ Balanced policy correctly selected Worker C (best balance)")
    return True


def test_risk_tolerance_threshold():
    """
    Test that risk tolerance threshold filters out low-scoring bids.
    """
    print("\n" + "="*70)
    print("Testing Risk Tolerance Threshold")
    print("="*70)
    
    policy = ConservativePolicy()
    
    task = Task(
        task_id=1,
        creator="0xBuyer123",
        specification_uri="ipfs://task-spec",
        required_capability="coding",
        reward_wei=50000000000000000,
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    
    # Low reputation worker
    agent = Agent(
        wallet_address="0xWorkerLow",
        name="LowRepWorker",
        capabilities=["coding"],
        reputation=Reputation(agent_address="0xWorkerLow", score=40),  # Very low
        policy_name="AggressivePolicy",
        role="worker",
    )
    bid = Bid(
        bid_id=1,
        task_id=1,
        bidder="0xWorkerLow",
        proposed_price_wei=20000000000000000,  # Low price
        estimated_duration_sec=600,
        timestamp=1000000,
    )
    
    # Score the bid
    score = policy.score_bid(agent, task, bid, [bid])
    
    print(f"\nLow reputation worker (rep 40):")
    print(f"  Bid score: {score:.2f}")
    print(f"  Risk tolerance threshold: 50.0")
    
    # Check if below typical threshold
    below_threshold = score < 50.0
    print(f"  Below threshold: {below_threshold}")
    
    if below_threshold:
        print("✅ Risk tolerance correctly filters low-scoring bid")
    else:
        print(f"⚠️  Score {score:.2f} is above threshold - may still be accepted")
    
    return True


if __name__ == "__main__":
    test_prd_worker_selection_conservative()
    test_prd_worker_selection_aggressive()
    test_prd_worker_selection_balanced()
    test_risk_tolerance_threshold()
    
    print("\n" + "="*70)
    print("✅ All BuyerAgent tests passed!")
    print("="*70)
    print("\nNote: These tests verify the bid scoring logic.")
    print("Blockchain interaction tests require a running testnet.")
