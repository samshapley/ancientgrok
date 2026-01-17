import sys
sys.path.insert(0, 'src')
import json

from clients.grok.client import GrokChatClient

print("Testing Complete Batch Translation Extraction")
print("="*50)

# Load the reference data to get texts
with open('data/sumerian_test.txt', 'r') as f:
    test_texts = [line.strip() for line in f if line.strip()][:500]

with open('data/english_test.txt', 'r') as f:
    test_refs = [line.strip() for line in f if line.strip()][:500]

print(f"Test set: {len(test_texts)} Sumerian texts")
print(f"References: {len(test_refs)} English translations\n")

# The batch was already run - just need to retrieve and parse results
# Simulate what translate_batch does by using the existing batch ID
batch_id = "batch_9a5613d7-da24-4503-b581-32469a9de811"

client = GrokChatClient(model="grok-4-1-fast-non-reasoning")

# Manually test the result retrieval with pagination
import httpx
import os

all_results = []
pagination_token = None

while True:
    results_url = f"https://api.x.ai/v1/batches/{batch_id}/results"
    if pagination_token:
        results_url += f"?pagination_token={pagination_token}"
    
    response = httpx.get(
        results_url,
        headers={"Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"},
        timeout=60.0
    )
    response.raise_for_status()
    data = response.json()
    
    all_results.extend(data.get("results", []))
    pagination_token = data.get("pagination_token")
    
    if not pagination_token:
        break

print(f"Retrieved {len(all_results)} results total\n")

# Now parse them using the same logic as translate_batch
from clients.unified.tools import TranslationTool

results_by_id = {}
for result_item in all_results:
    custom_id = result_item.get("batch_request_id")
    
    batch_result = result_item.get("batch_result", {})
    response_wrapper = batch_result.get("response", {})
    response_data = response_wrapper.get("chat_get_completion", {})
    
    if not response_data:
        results_by_id[custom_id] = {"error": "No completion data"}
        continue
    
    if "choices" in response_data:
        choice = response_data["choices"][0]
        
        if "message" in choice and "tool_calls" in choice["message"]:
            for tool_call in choice["message"]["tool_calls"]:
                if tool_call["function"]["name"] == "translate_text":
                    args = json.loads(tool_call["function"]["arguments"])
                    results_by_id[custom_id] = {
                        "translation": args["translation"],
                        "confidence": args.get("confidence", "medium")
                    }
                    break

# Build final results in order
final_results = []
for i in range(500):
    custom_id = f"trans_{i}"
    if custom_id in results_by_id:
        final_results.append(results_by_id[custom_id])
    else:
        final_results.append({"error": "Missing"})

# Count successes vs errors
succ = sum(1 for r in final_results if "translation" in r)
err = sum(1 for r in final_results if "error" in r)

print(f"Parsed Results:")
print(f"  Successful: {succ} ({succ/500*100:.1f}%)")
print(f"  Errors: {err} ({err/500*100:.1f}%)")

if succ > 0:
    print(f"\nFirst 3 successful translations:")
    shown = 0
    for i, r in enumerate(final_results):
        if "translation" in r and shown < 3:
            print(f"  {i}. {test_texts[i][:30]}... → {r['translation'][:50]}...")
            shown += 1
