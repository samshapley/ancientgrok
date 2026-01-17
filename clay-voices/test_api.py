"""Quick test of the Claude API client with structured outputs."""

import sys
sys.path.insert(0, 'src')

from api_clients import ClaudeClient
from data_loader import ParallelCorpus

def test_claude_client():
    """Test Claude client with a few Sumerian examples."""
    print("="*70)
    print("ClayVoices API Test")
    print("="*70)
    
    # Load data
    print("\nLoading dataset...")
    corpus = ParallelCorpus("data")
    print(f"Dataset stats: {corpus.stats()}")
    
    # Initialize client
    print("\nInitializing Claude client...")
    client = ClaudeClient(model="claude-sonnet-4-20250514")
    
    # Get a few test examples
    test_examples = corpus.test_pairs[:3]
    few_shot = corpus.sample_few_shot(3)
    
    print(f"\nFew-shot examples ({len(few_shot)}):")
    for i, (sum_text, eng_text) in enumerate(few_shot, 1):
        print(f"{i}. {sum_text[:60]}... → {eng_text[:60]}...")
    
    print("\n" + "="*70)
    print("Running translations...")
    print("="*70)
    
    for i, (sumerian, reference) in enumerate(test_examples, 1):
        print(f"\n[Test {i}/3]")
        print(f"Sumerian: {sumerian}")
        print(f"Reference: {reference}")
        
        # Translate with structured output
        result = client.translate(
            sumerian,
            few_shot_examples=few_shot,
            use_structured_output=True
        )
        
        print(f"Translation: {result['translation']}")
        print(f"Confidence: {result['confidence']}")
        if result['notes']:
            print(f"Notes: {result['notes']}")
        print(f"Tokens: {result['usage']['input_tokens']} in, {result['usage']['output_tokens']} out")
    
    print("\n" + "="*70)
    print("Test completed successfully!")
    print("="*70)

if __name__ == "__main__":
    test_claude_client()