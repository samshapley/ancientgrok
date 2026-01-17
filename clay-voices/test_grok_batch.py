import os
import sys
sys.path.insert(0, 'src')

from clients.grok.client import GrokChatClient

# Test batch with 3 examples
test_texts = [
    "lugal kur-kur-ra",
    "en šul ša3-ga-na",  
    "udu 10"
]

print("Testing Grok batch API with 3 requests...")
print("="*50)

client = GrokChatClient(model="grok-4-1-fast-non-reasoning")

try:
    results = client.translate_batch(
        test_texts,
        few_shot_examples=[],
        poll_interval=10.0,
        timeout=300.0
    )
    
    print(f"\n✅ Batch completed successfully!")
    print(f"Results: {len(results)} translations")
    
    for i, result in enumerate(results):
        print(f"\n{i+1}. {test_texts[i]}")
        print(f"   Translation: {result['translation']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Tokens: {result['usage']['input_tokens']} in, {result['usage']['output_tokens']} out")
        
except Exception as e:
    print(f"\n❌ Batch API test failed: {e}")
    import traceback
    traceback.print_exc()
