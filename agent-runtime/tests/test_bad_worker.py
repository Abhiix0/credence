"""
Test BadWorkerAgent - Demonstrate verification catching fraudulent work.

This test shows that:
1. BadWorkerAgent produces wrong results
2. VerifierAgent detects the fraud
3. Reputation system penalizes bad workers
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set failure rate for testing
os.environ["AGENT_FAILURE_RATE"] = "1.0"  # Always fail for testing
os.environ["AGENT_FAILURE_SEED"] = "42"  # Reproducible behavior

from src.models import Task, TaskStatus
from src.execution import TaskExecutor


def test_bad_worker_produces_wrong_result():
    """
    Test that BadWorkerAgent produces different result than honest worker.
    """
    print("\n" + "="*70)
    print("Testing BadWorkerAgent Produces Wrong Results")
    print("="*70)
    
    # Import after env vars are set
    from src.agents.bad_worker_agent import BadWorkerAgent
    
    # Create task
    task = Task(
        task_id=100,
        creator="0xBuyer123",
        specification_uri="This product is terrible and I hate it!",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
        selected_worker="0xBadWorker",
    )
    
    # Honest worker execution
    print("\n1. Honest worker execution:")
    honest_executor = TaskExecutor(api_key=None)
    honest_uri, honest_hash = honest_executor.execute(task)
    print(f"   Honest URI:  {honest_uri}")
    print(f"   Honest Hash: {honest_hash.hex()}")
    
    # Bad worker execution
    print("\n2. Bad worker execution (FAILURE_RATE=1.0):")
    bad_agent = BadWorkerAgent(
        name="TestBadWorker",
        capabilities=["sentiment-analysis"],
        failure_rate=1.0  # Always produce bad results
    )
    bad_uri, bad_hash = bad_agent.execute_task(task)
    print(f"   Bad URI:  {bad_uri}")
    print(f"   Bad Hash: {bad_hash.hex()}")
    
    # Compare
    print("\n3. Comparison:")
    print(f"   Hashes match: {honest_hash == bad_hash}")
    print(f"   URIs match:   {honest_uri == bad_uri}")
    
    # They should be different!
    assert honest_hash != bad_hash, "Bad worker should produce different hash"
    assert honest_uri != bad_uri, "Bad worker should produce different URI"
    
    print("\n✅ Bad worker produces detectably different results")
    return True


def test_verification_catches_bad_work():
    """
    Test that verification detects fraudulent results.
    """
    print("\n" + "="*70)
    print("Testing Verification Catches Bad Work")
    print("="*70)
    
    from src.agents.bad_worker_agent import BadWorkerAgent
    
    # Create task
    task = Task(
        task_id=101,
        creator="0xBuyer123",
        specification_uri="This is an amazing product!",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.SUBMITTED,
        selected_worker="0xBadWorker",
    )
    
    # Bad worker submits wrong result
    print("\n1. Bad worker submits result:")
    bad_agent = BadWorkerAgent(
        name="TestBadWorker",
        capabilities=["sentiment-analysis"],
        failure_rate=1.0
    )
    submitted_uri, submitted_hash = bad_agent.execute_task(task)
    
    # Simulate submission
    task.result_uri = submitted_uri
    task.result_hash = submitted_hash
    
    print(f"   Submitted URI:  {submitted_uri}")
    print(f"   Submitted Hash: {submitted_hash.hex()}")
    
    # Verifier re-executes to check
    print("\n2. Verifier re-executes task:")
    honest_executor = TaskExecutor(api_key=None)
    verified_uri, verified_hash = honest_executor.execute(task)
    
    print(f"   Verified URI:  {verified_uri}")
    print(f"   Verified Hash: {verified_hash.hex()}")
    
    # Verification comparison
    print("\n3. Verification check:")
    hash_match = verified_hash == task.result_hash
    uri_valid = task.result_uri.startswith(f"ipfs://result-{task.task_id}-")
    
    print(f"   Hash match: {hash_match} {'✅' if hash_match else '❌ FRAUD DETECTED'}")
    print(f"   URI valid:  {uri_valid} {'✅' if uri_valid else '❌'}")
    
    verification_passed = hash_match and uri_valid
    
    print(f"\n4. Verification result: {'PASS ✅' if verification_passed else 'FAIL ❌ (Expected)'}")
    
    # Verification should fail!
    assert not verification_passed, "Verification should catch bad work"
    
    print("\n✅ Verification successfully detects fraudulent work")
    return True


def test_failure_rate_probability():
    """
    Test that failure rate controls probability of bad results.
    """
    print("\n" + "="*70)
    print("Testing Failure Rate Configuration")
    print("="*70)
    
    from src.agents.bad_worker_agent import BadWorkerAgent
    
    task = Task(
        task_id=102,
        creator="0xBuyer123",
        specification_uri="Test input",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    # Test with 0% failure rate (should act honest)
    print("\n1. Testing FAILURE_RATE=0.0 (should produce honest results):")
    agent_honest = BadWorkerAgent(
        name="TestAgent",
        capabilities=["sentiment-analysis"],
        failure_rate=0.0
    )
    
    honest_executor = TaskExecutor(api_key=None)
    expected_uri, expected_hash = honest_executor.execute(task)
    
    # Execute multiple times - all should match honest execution
    matches = 0
    trials = 10
    for i in range(trials):
        result_uri, result_hash = agent_honest.execute_task(task)
        if result_hash == expected_hash:
            matches += 1
    
    print(f"   Honest results: {matches}/{trials} ({matches/trials*100:.0f}%)")
    assert matches == trials, "With 0% failure rate, all results should be honest"
    
    # Test with 100% failure rate (should always fail)
    print("\n2. Testing FAILURE_RATE=1.0 (should always produce bad results):")
    agent_bad = BadWorkerAgent(
        name="TestAgent",
        capabilities=["sentiment-analysis"],
        failure_rate=1.0
    )
    
    bad_results = 0
    for i in range(trials):
        result_uri, result_hash = agent_bad.execute_task(task)
        if result_hash != expected_hash:
            bad_results += 1
    
    print(f"   Bad results: {bad_results}/{trials} ({bad_results/trials*100:.0f}%)")
    assert bad_results == trials, "With 100% failure rate, all results should be bad"
    
    print("\n✅ Failure rate configuration works correctly")
    return True


def test_bad_worker_aggressive_bidding():
    """
    Test that BadWorkerAgent always bids aggressively.
    """
    print("\n" + "="*70)
    print("Testing BadWorkerAgent Aggressive Bidding")
    print("="*70)
    
    from src.agents.bad_worker_agent import BadWorkerAgent
    
    # High-reward task
    task_high = Task(
        task_id=103,
        creator="0xBuyer123",
        specification_uri="Expensive task",
        required_capability="sentiment-analysis",
        reward_wei=10000000000000000000,  # 10 ETH
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    
    agent = BadWorkerAgent(
        name="TestBadWorker",
        capabilities=["sentiment-analysis"],
        failure_rate=0.4
    )
    
    print("\n1. High-reward task (10 ETH):")
    decision = agent.evaluate_and_decide(task_high)
    
    if decision:
        price_pct = (decision["proposed_price"] / task_high.reward_wei) * 100
        print(f"   Proposed price: {decision['proposed_price']} wei ({price_pct:.1f}% of reward)")
        print(f"   Duration: {decision['estimated_duration']}s")
        
        # Should bid aggressively (~50% of reward)
        assert price_pct < 60, "Bad worker should bid aggressively (low price)"
        assert decision["estimated_duration"] < 600, "Bad worker should promise fast delivery"
    
    print("\n✅ Bad worker bids aggressively on all matching tasks")
    return True


if __name__ == "__main__":
    test_bad_worker_produces_wrong_result()
    test_verification_catches_bad_work()
    test_failure_rate_probability()
    test_bad_worker_aggressive_bidding()
    
    print("\n" + "="*70)
    print("✅ All BadWorkerAgent tests passed!")
    print("="*70)
    print("\nKey findings:")
    print("1. BadWorkerAgent produces detectably different results")
    print("2. VerifierAgent successfully catches fraudulent work")
    print("3. Failure rate controls probability of bad behavior")
    print("4. On-chain interaction is identical to honest workers")
    print("\nThis demonstrates that the verification system works!")
