"""
Test VerifierAgent verification logic (without blockchain interaction).
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Task, TaskStatus
from src.execution import TaskExecutor


def test_hash_verification_logic():
    """
    Test the core verification logic: re-execute task and compare hashes.
    
    This tests the verification algorithm without requiring blockchain connection.
    """
    print("\n" + "="*60)
    print("Testing VerifierAgent Hash Verification Logic")
    print("="*60)
    
    executor = TaskExecutor(api_key=None)  # Use fallback mode
    
    # Create a test task
    task = Task(
        task_id=100,
        creator="0xBuyer123",
        specification_uri="This product is absolutely amazing!",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.SUBMITTED,
    )
    
    # Worker executes task and submits result
    print("\n1. Worker executes task:")
    worker_uri, worker_hash = executor.execute(task)
    print(f"   Worker URI:  {worker_uri}")
    print(f"   Worker Hash: {worker_hash.hex()}")
    
    # Simulate worker submitting to blockchain
    task.result_uri = worker_uri
    task.result_hash = worker_hash
    
    # Verifier re-executes to verify
    print("\n2. Verifier re-executes task:")
    verifier_uri, verifier_hash = executor.execute(task)
    print(f"   Verifier URI:  {verifier_uri}")
    print(f"   Verifier Hash: {verifier_hash.hex()}")
    
    # Verification logic
    print("\n3. Verification checks:")
    hash_match = verifier_hash == task.result_hash
    uri_valid = task.result_uri.startswith(f"ipfs://result-{task.task_id}-")
    hash_in_uri = task.result_hash.hex()[:12] in task.result_uri
    
    print(f"   Hash match:        {hash_match} {'✅' if hash_match else '❌'}")
    print(f"   URI format valid:  {uri_valid} {'✅' if uri_valid else '❌'}")
    print(f"   Hash in URI:       {hash_in_uri} {'✅' if hash_in_uri else '❌'}")
    
    verification_passed = hash_match and uri_valid and hash_in_uri
    
    print(f"\n4. Verification result: {'PASS ✅' if verification_passed else 'FAIL ❌'}")
    
    assert verification_passed, "Verification should pass for honest worker"
    
    print("\n✅ Hash verification logic test passed!")
    return verification_passed


def test_fraud_detection():
    """
    Test that verifier detects fraudulent/incorrect submissions.
    """
    print("\n" + "="*60)
    print("Testing Fraud Detection")
    print("="*60)
    
    executor = TaskExecutor(api_key=None)
    
    task = Task(
        task_id=101,
        creator="0xBuyer123",
        specification_uri="This is terrible and I hate it!",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.SUBMITTED,
    )
    
    # Honest execution
    correct_uri, correct_hash = executor.execute(task)
    print(f"\n1. Correct result:")
    print(f"   URI:  {correct_uri}")
    print(f"   Hash: {correct_hash.hex()}")
    
    # Simulate fraudulent worker submitting wrong hash
    fake_hash = b'\xde\xad\xbe\xef' * 8  # Fake 32-byte hash
    fake_uri = f"ipfs://result-{task.task_id}-{fake_hash.hex()[:12]}"
    
    task.result_uri = fake_uri
    task.result_hash = fake_hash
    
    print(f"\n2. Fraudulent submission:")
    print(f"   URI:  {fake_uri}")
    print(f"   Hash: {fake_hash.hex()}")
    
    # Verifier re-executes
    verifier_uri, verifier_hash = executor.execute(task)
    print(f"\n3. Verifier computes:")
    print(f"   URI:  {verifier_uri}")
    print(f"   Hash: {verifier_hash.hex()}")
    
    # Verification should fail
    hash_match = verifier_hash == task.result_hash
    print(f"\n4. Hash match: {hash_match} {'✅' if hash_match else '❌ (Expected - fraud detected)'}")
    
    verification_passed = hash_match
    
    print(f"\n5. Verification result: {'PASS' if verification_passed else 'FAIL ❌ (Expected - fraud detected)'}")
    
    assert not verification_passed, "Verification should fail for fraudulent submission"
    
    print("\n✅ Fraud detection test passed!")
    return not verification_passed


def test_uri_format_validation():
    """
    Test URI format validation (lighter verification method).
    """
    print("\n" + "="*60)
    print("Testing URI Format Validation")
    print("="*60)
    
    executor = TaskExecutor(api_key=None)
    
    task = Task(
        task_id=102,
        creator="0xBuyer123",
        specification_uri="Test input",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.SUBMITTED,
    )
    
    # Execute to get correct result
    correct_uri, correct_hash = executor.execute(task)
    
    print("\n1. Valid submission:")
    task.result_uri = correct_uri
    task.result_hash = correct_hash
    
    # Check URI format
    uri_valid = task.result_uri.startswith(f"ipfs://result-{task.task_id}-")
    uri_hash_prefix = task.result_uri.split("-")[-1]
    actual_hash_prefix = task.result_hash.hex()[:12]
    hash_prefix_match = uri_hash_prefix == actual_hash_prefix
    
    print(f"   URI: {task.result_uri}")
    print(f"   URI pattern valid: {uri_valid} {'✅' if uri_valid else '❌'}")
    print(f"   Hash prefix match: {hash_prefix_match} {'✅' if hash_prefix_match else '❌'}")
    
    assert uri_valid and hash_prefix_match, "Valid URI should pass format check"
    
    print("\n2. Invalid submission (wrong task ID in URI):")
    invalid_uri = f"ipfs://result-999-{correct_hash.hex()[:12]}"
    task.result_uri = invalid_uri
    
    uri_valid = task.result_uri.startswith(f"ipfs://result-{task.task_id}-")
    print(f"   URI: {task.result_uri}")
    print(f"   URI pattern valid: {uri_valid} {'❌' if not uri_valid else '✅'}")
    
    assert not uri_valid, "Invalid URI should fail format check"
    
    print("\n✅ URI format validation test passed!")


def test_deterministic_verification():
    """
    Test that verification is deterministic (same input -> same result).
    """
    print("\n" + "="*60)
    print("Testing Deterministic Verification")
    print("="*60)
    
    executor = TaskExecutor(api_key=None)
    
    task = Task(
        task_id=103,
        creator="0xBuyer123",
        specification_uri="Consistent test input",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.SUBMITTED,
    )
    
    # Execute multiple times
    print("\n1. First execution:")
    uri_1, hash_1 = executor.execute(task)
    print(f"   Hash: {hash_1.hex()}")
    
    print("\n2. Second execution:")
    uri_2, hash_2 = executor.execute(task)
    print(f"   Hash: {hash_2.hex()}")
    
    print("\n3. Third execution:")
    uri_3, hash_3 = executor.execute(task)
    print(f"   Hash: {hash_3.hex()}")
    
    # All should be identical
    all_match = (hash_1 == hash_2 == hash_3) and (uri_1 == uri_2 == uri_3)
    
    print(f"\n4. All results identical: {all_match} {'✅' if all_match else '❌'}")
    
    assert all_match, "Verification must be deterministic"
    
    print("\n✅ Deterministic verification test passed!")


if __name__ == "__main__":
    test_hash_verification_logic()
    test_fraud_detection()
    test_uri_format_validation()
    test_deterministic_verification()
    
    print("\n" + "="*60)
    print("✅ All VerifierAgent tests passed!")
    print("="*60)
