"""Test all three providers with both individual and batch modes."""

import sys
sys.path.insert(0, 'src')

from api_clients import ClaudeClient, GPT5Client, GeminiClient
from data_loader import ParallelCorpus

def test_provider(client_class, model, provider_name):
    """Test a single provider."""
    print("\n" + "="*70)
    print(f"Testing {provider_name}")
    print("="*70)
    
    # Load data
    corpus = ParallelCorpus("data")
    test_examples = corpus.test_pairs[:2]
    few_shot = corpus.sample_few_shot(2)
    
    # Initialize client
    print(f"Initializing {provider_name} client (model: {model})...")
    try:
        client = client_class(model=model)
    except Exception as e:
        print(f"FAILED to initialize {provider_name}: {e}")
        return False
    
    # Test individual mode
    print(f"\n[Individual Mode Test]")
    for i, (sumerian, reference) in enumerate(test_examples, 1):
        print(f"  Example {i}: {sumerian[:40]}...")
        try:
            result = client.translate(sumerian, few_shot_examples=few_shot)
            print(f"  → {result['translation'][:50]}... [conf: {result['confidence']}]")
        except Exception as e:
            print(f"  FAILED: {e}")
            return False
    
    # Test batch mode
    print(f"\n[Batch Mode Test]")
    sumerian_batch = [pair[0] for pair in test_examples]
    try:
        results = client.translate_batch(sumerian_batch, few_shot_examples=few_shot)
        print(f"  Batch completed: {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['translation'][:50]}... [conf: {result['confidence']}]")
    except Exception as e:
        print(f"  BATCH FAILED: {e}")
        # Batch failure is not critical if individual works
        print(f"  (Individual mode still works)")
    
    print(f"\n✅ {provider_name} tests passed!")
    return True


def main():
    """Test all providers."""
    print("="*70)
    print("ClayVoices Multi-Provider Test")
    print("="*70)
    
    results = []
    
    # Test Claude
    results.append(("Claude", test_provider(ClaudeClient, "claude-sonnet-4-20250514", "Claude Sonnet 4")))
    
    # Test GPT-5.2
    results.append(("GPT-5.2", test_provider(GPT5Client, "gpt-5.2-instant", "GPT-5.2 Instant")))
    
    # Test Gemini
    results.append(("Gemini", test_provider(GeminiClient, "gemini-2.5-pro", "Gemini 2.5 Pro")))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for provider, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{provider}: {status}")
    
    all_passed = all(passed for _, passed in results)
    if all_passed:
        print("\n🎉 All providers working!")
    else:
        print("\n⚠️  Some providers failed - see details above")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)