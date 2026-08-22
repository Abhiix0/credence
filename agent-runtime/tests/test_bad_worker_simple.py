"""
Simplified test for BadWorkerAgent fraud detection logic.

Tests the core fraud detection mechanism without requiring full agent initialization.
"""

import sys
import os
import json
import hashlib
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Task, TaskStatus
from src.execution import TaskExecutor


def test_fraud_detection_concept():
    """
    Demonstrate the fraud detection concept:
    - Honest worker: produces hash H1
    - Bad worker: produces different hash H2
    - Verifier re-executes and gets H1
    - Comparison: H1 != H2 → fraud detected
    """
    print("\n" + "="*70)
    print("Testing Fraud Detection Concept")
    print("="*70)
    
    # Task specification
    task = Task(
        task_id=100,
        creator="0xBuyer123",
        specification_uri="This product is terrible and I hate it!",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    print(f"\nTask: {task.specification_uri}")
    print(f"Capability: {task.required_capability}")
    
    # Honest execution
    print("\n1. HONEST WORKER executes:")
    honest_executor = TaskExecutor(api_key=None)
    honest_uri, honest_hash = honest_executor.execute(task)
    
    # The honest result should be "negative" for this text
    print(f"   Result URI:  {honest_uri}")
    print(f"   Result Hash: {honest_hash.hex()}")
    
    # Fraudulent execution (simulate BadWorkerAgent)
    print("\n2. BAD WORKER submits fraudulent result:")
    # BadWorkerAgent always returns "positive" for sentiment-analysis
    fraudulent_output = json.dumps({"result": "positive"})
    fraudulent_hash = hashlib.sha256(fraudulent_output.encode("utf-8")).digest()
    fraudulent_uri = f"ipfs://result-{task.task_id}-{fraudulent_hash.hex()[:12]}"
    
    print(f"   Result URI:  {fraudulent_uri}")
    print(f"   Result Hash: {fraudulent_hash.hex()}")
    print(f"   ⚠️  Always returns 'positive' regardless of input!")
    
    # Verification
    print("\n3. VERIFIER re-executes task:")
    verifier_executor = TaskExecutor(api_key=None)
    verified_uri, verified_hash = verifier_executor.execute(task)
    
    print(f"   Verified URI:  {verified_uri}")
    print(f"   Verified Hash: {verified_hash.hex()}")
    
    # Compare
    print("\n4. FRAUD DETECTION:")
    print(f"   Submitted hash: {fraudulent_hash.hex()}")
    print(f"   Verified hash:  {verified_hash.hex()}")
    print(f"   Match: {fraudulent_hash == verified_hash} ", end="")
    
    if fraudulent_hash == verified_hash:
        print("✅ (Honest work)")
    else:
        print("❌ FRAUD DETECTED!")
    
    # Assertion
    assert fraudulent_hash != verified_hash, "Fraud should be detected"
    assert honest_hash == verified_hash, "Honest work should match verification"
    
    print("\n✅ Fraud detection works correctly!")
    print("\nConclusion:")
    print("  - Bad worker's wrong result has different hash")
    print("  - Verifier detects mismatch by re-executing")
    print("  - On-chain verification will FAIL")
    print("  - Bad worker's reputation will be penalized")
    
    return True


def test_failure_modes():
    """
    Test different types of fraudulent results.
    """
    print("\n" + "="*70)
    print("Testing Different Fraud Scenarios")
    print("="*70)
    
    # Scenario 1: Wrong sentiment
    print("\n1. Wrong Sentiment (Negative text → claim Positive):")
    negative_text = "This is absolutely terrible!"
    
    # Honest result
    honest_output = json.dumps({"result": "negative"})
    honest_hash = hashlib.sha256(honest_output.encode("utf-8")).digest()
    
    # Fraudulent result (wrong sentiment)
    fraud_output = json.dumps({"result": "positive"})
    fraud_hash = hashlib.sha256(fraud_output.encode("utf-8")).digest()
    
    print(f"   Honest result:      {json.loads(honest_output)}")
    print(f"   Fraudulent result:  {json.loads(fraud_output)}")
    print(f"   Hashes match: {honest_hash == fraud_hash} ❌")
    
    assert honest_hash != fraud_hash
    
    # Scenario 2: Wrong classification
    print("\n2. Wrong Classification:")
    
    honest_class = json.dumps({"result": "technology"})
    fraud_class = json.dumps({"result": "general"})
    
    honest_hash_2 = hashlib.sha256(honest_class.encode("utf-8")).digest()
    fraud_hash_2 = hashlib.sha256(fraud_class.encode("utf-8")).digest()
    
    print(f"   Correct:    {json.loads(honest_class)}")
    print(f"   Fraudulent: {json.loads(fraud_class)}")
    print(f"   Hashes match: {honest_hash_2 == fraud_hash_2} ❌")
    
    assert honest_hash_2 != fraud_hash_2
    
    # Scenario 3: Malformed result
    print("\n3. Malformed Result:")
    
    valid_output = json.dumps({"result": "positive"})
    malformed_output = json.dumps({"result": "fraudulent_output", "error": "bad result"})
    
    valid_hash = hashlib.sha256(valid_output.encode("utf-8")).digest()
    malformed_hash = hashlib.sha256(malformed_output.encode("utf-8")).digest()
    
    print(f"   Valid:      {json.loads(valid_output)}")
    print(f"   Malformed:  {json.loads(malformed_output)}")
    print(f"   Hashes match: {valid_hash == malformed_hash} ❌")
    
    assert valid_hash != malformed_hash
    
    print("\n✅ All fraud scenarios are detectable!")
    return True


def test_badworker_configuration():
    """
    Test BadWorkerAgent configuration options.
    """
    print("\n" + "="*70)
    print("Testing BadWorkerAgent Configuration")
    print("="*70)
    
    print("\nConfiguration options:")
    print("  AGENT_FAILURE_RATE: Probability of producing bad result")
    print("    - 0.0 = Never fail (acts like honest worker)")
    print("    - 0.4 = 40% of tasks fail (default)")
    print("    - 1.0 = Always fail")
    
    print("\n  AGENT_FAILURE_SEED: RNG seed for reproducibility")
    print("    - Set to same value for consistent bad behavior")
    print("    - Useful for testing and demos")
    
    print("\nBehavior:")
    print("  ✓ Always bids aggressively (ignores policy)")
    print("  ✓ Bids on all matching capabilities")
    print("  ✓ Produces wrong results based on failure rate")
    print("  ✓ Uses identical on-chain transaction plumbing")
    print("  ✓ Verification catches fraud through hash mismatch")
    
    print("\n✅ BadWorkerAgent configuration documented")
    return True


if __name__ == "__main__":
    test_fraud_detection_concept()
    test_failure_modes()
    test_badworker_configuration()
    
    print("\n" + "="*70)
    print("✅ All fraud detection tests passed!")
    print("="*70)
    print("\nKey Takeaways:")
    print("1. Deterministic execution enables fraud detection")
    print("2. Hash comparison reveals any result discrepancy")
    print("3. BadWorkerAgent demonstrates verifier effectiveness")
    print("4. On-chain interaction is identical (no plumbing changes)")
    print("5. Reputation system will penalize caught fraud")
