"""
Test TaskExecutor capability-based routing and fallback behavior.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Task, TaskStatus
from src.execution import TaskExecutor


def test_sentiment_analysis_fallback():
    """Test sentiment analysis with fallback classifier (no Gemini)."""
    
    # Create executor without API key to force fallback
    executor = TaskExecutor(api_key=None)
    
    # Test positive sentiment
    task_positive = Task(
        task_id=1,
        creator="0xBuyer",
        specification_uri="This product is amazing and I love it!",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    result_uri, result_hash = executor.execute(task_positive)
    
    print(f"Positive sentiment test:")
    print(f"  Result URI: {result_uri}")
    print(f"  Result Hash: {result_hash.hex()}")
    
    # Verify result structure
    assert result_uri.startswith("ipfs://result-1-")
    assert len(result_hash) == 32  # SHA256 = 32 bytes
    assert result_hash.hex()[:12] in result_uri
    
    # Test negative sentiment
    task_negative = Task(
        task_id=2,
        creator="0xBuyer",
        specification_uri="This is terrible and I hate it!",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    result_uri, result_hash = executor.execute(task_negative)
    
    print(f"\nNegative sentiment test:")
    print(f"  Result URI: {result_uri}")
    print(f"  Result Hash: {result_hash.hex()}")
    
    assert result_uri.startswith("ipfs://result-2-")
    assert len(result_hash) == 32
    
    # Test neutral sentiment
    task_neutral = Task(
        task_id=3,
        creator="0xBuyer",
        specification_uri="The sky is blue.",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    result_uri, result_hash = executor.execute(task_neutral)
    
    print(f"\nNeutral sentiment test:")
    print(f"  Result URI: {result_uri}")
    print(f"  Result Hash: {result_hash.hex()}")
    
    assert result_uri.startswith("ipfs://result-3-")
    assert len(result_hash) == 32
    
    print("\n✅ Sentiment analysis fallback tests passed!")


def test_classification_fallback():
    """Test classification with fallback (no Gemini)."""
    
    executor = TaskExecutor(api_key=None)
    
    # Test with JSON specification
    spec = {
        "text": "Python is a programming language",
        "categories": ["technology", "sports", "politics", "entertainment"]
    }
    
    task = Task(
        task_id=4,
        creator="0xBuyer",
        specification_uri=json.dumps(spec),
        required_capability="classification",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    result_uri, result_hash = executor.execute(task)
    
    print(f"\nClassification test:")
    print(f"  Result URI: {result_uri}")
    print(f"  Result Hash: {result_hash.hex()}")
    
    assert result_uri.startswith("ipfs://result-4-")
    assert len(result_hash) == 32
    
    print("\n✅ Classification fallback test passed!")


def test_unknown_capability():
    """Test generic execution for unknown capability."""
    
    executor = TaskExecutor(api_key=None)
    
    task = Task(
        task_id=5,
        creator="0xBuyer",
        specification_uri="Some task specification",
        required_capability="unknown-capability",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    result_uri, result_hash = executor.execute(task)
    
    print(f"\nUnknown capability test:")
    print(f"  Result URI: {result_uri}")
    print(f"  Result Hash: {result_hash.hex()}")
    
    assert result_uri.startswith("ipfs://result-5-")
    assert len(result_hash) == 32
    
    print("\n✅ Unknown capability test passed!")


def test_hash_consistency():
    """Test that same input produces same hash."""
    
    executor = TaskExecutor(api_key=None)
    
    task = Task(
        task_id=6,
        creator="0xBuyer",
        specification_uri="Consistent input text",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    # Execute twice
    result_uri_1, result_hash_1 = executor.execute(task)
    result_uri_2, result_hash_2 = executor.execute(task)
    
    print(f"\nHash consistency test:")
    print(f"  First hash:  {result_hash_1.hex()}")
    print(f"  Second hash: {result_hash_2.hex()}")
    print(f"  Match: {result_hash_1 == result_hash_2}")
    
    # Hashes should be identical for same input
    assert result_hash_1 == result_hash_2
    assert result_uri_1 == result_uri_2
    
    print("\n✅ Hash consistency test passed!")


def test_with_gemini_api_key():
    """Test with Gemini API key if available."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("\n⚠️  GEMINI_API_KEY not set, skipping Gemini integration test")
        return
    
    executor = TaskExecutor(api_key=api_key)
    
    if not executor.genai_client:
        print("\n⚠️  Gemini client failed to initialize, skipping Gemini integration test")
        return
    
    print("\n🔑 Testing with Gemini API...")
    
    task = Task(
        task_id=7,
        creator="0xBuyer",
        specification_uri="This movie was absolutely fantastic and entertaining!",
        required_capability="sentiment-analysis",
        reward_wei=1000000000000000000,
        deadline=9999999999,
        status=TaskStatus.ASSIGNED,
    )
    
    result_uri, result_hash = executor.execute(task)
    
    print(f"  Result URI: {result_uri}")
    print(f"  Result Hash: {result_hash.hex()}")
    
    assert result_uri.startswith("ipfs://result-7-")
    assert len(result_hash) == 32
    
    print("\n✅ Gemini integration test passed!")


if __name__ == "__main__":
    test_sentiment_analysis_fallback()
    test_classification_fallback()
    test_unknown_capability()
    test_hash_consistency()
    test_with_gemini_api_key()
    
    print("\n" + "="*50)
    print("✅ All executor tests passed!")
    print("="*50)
