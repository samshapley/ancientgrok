import sys
sys.path.insert(0, 'src')

from clients.grok.client import GrokChatClient
from evaluator import TranslationEvaluator

print("Testing Grok → BLEU Evaluation Pipeline")
print("="*50)

# Minimal test data
test_cases = [
    ("lugal kur-kur-ra", "king of the lands"),
    ("udu 10", "10 sheep"),
    ("še gur 5", "5 gur of barley")
]

sumerian_texts = [s for s, _ in test_cases]
references = [e for _, e in test_cases]

print(f"Test set: {len(test_cases)} examples\n")

# Translate with Grok (individual API for speed)
print("Step 1: Translating with Grok...")
client = GrokChatClient(model="grok-4-1-fast-non-reasoning")

predictions = []
for i, text in enumerate(sumerian_texts):
    try:
        result = client.translate(text, few_shot_examples=[])
        predictions.append(result["translation"])
        print(f"  {i+1}. {text} → {result['translation']}")
    except Exception as e:
        print(f"  {i+1}. ERROR: {e}")
        predictions.append("")  # Empty on error

print(f"\nStep 2: Evaluating with BLEU...")
evaluator = TranslationEvaluator()

# Compute BLEU score
try:
    metrics = evaluator.evaluate(predictions, references, [])
    
    print("\n✅ BLEU Evaluation Successful!")
    print(f"BLEU Score: {metrics['bleu']['score']:.2f}")
    print(f"chrF Score: {metrics['chrf']['score']:.2f}")
    
    print("\nPer-example scores:")
    for i, (pred, ref) in enumerate(zip(predictions, references)):
        print(f"  {i+1}. Pred: '{pred}' | Ref: '{ref}'")
    
except Exception as e:
    print(f"\n❌ BLEU Evaluation Failed: {e}")
    import traceback
    traceback.print_exc()
