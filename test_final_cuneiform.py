import sys
sys.path.insert(0, 'src')

# Force reload to get latest code
import importlib
if 'ancientgrok.cuneiform_tools' in sys.modules:
    del sys.modules['ancientgrok.cuneiform_tools']

from ancientgrok.cuneiform_tools import lookup_cuneiform_sign, list_cuneiform_signs

# Test sign lookup
result = lookup_cuneiform_sign('A', 'name')
print(f"Lookup 'A' by name:")
print(f"  Found: {result.get('found')}")
print(f"  Total database: {result.get('total_database_size')}")
print(f"  Matches: {result.get('count')}")
if result.get('matches'):
    print(f"  First match: {result['matches'][0]}")

# Test listing
list_result = list_cuneiform_signs(limit=5)
print(f"\nList 5 signs:")
print(f"  Total: {list_result.get('total')}")
print(f"  Showing: {list_result.get('showing')}")
if list_result.get('signs'):
    for sign in list_result['signs']:
        print(f"  - {sign['code_point']}: {sign['name']} ({sign['character']})")
