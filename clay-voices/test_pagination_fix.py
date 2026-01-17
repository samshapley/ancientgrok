import sys
sys.path.insert(0, 'src')
import httpx
import os

# Test pagination manually
batch_id = "batch_9a5613d7-da24-4503-b581-32469a9de811"
api_key = os.getenv("XAI_API_KEY")

all_results = []
pagination_token = None
page_num = 1

print("Testing result pagination...")
print("="*50)

while True:
    results_url = f"https://api.x.ai/v1/batches/{batch_id}/results"
    if pagination_token:
        results_url += f"?pagination_token={pagination_token}"
    
    response = httpx.get(
        results_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=60.0
    )
    response.raise_for_status()
    data = response.json()
    
    page_results = data.get("results", [])
    all_results.extend(page_results)
    
    print(f"Page {page_num}: {len(page_results)} results (total so far: {len(all_results)})")
    
    pagination_token = data.get("pagination_token")
    if not pagination_token:
        print("No more pages - pagination complete")
        break
    
    page_num += 1
    
    if page_num > 10:  # Safety limit
        print("Safety limit reached")
        break

print(f"\n✅ Total results retrieved: {len(all_results)}")
print(f"Expected: 500")
print(f"Match: {len(all_results) == 500}")
