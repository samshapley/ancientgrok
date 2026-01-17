import sys
from pathlib import Path

# Fresh import after code changes
import importlib
sys.path.insert(0, 'src')

# Import and reload to get latest code
import ancientgrok.cuneiform_tools
importlib.reload(ancientgrok.cuneiform_tools)
from ancientgrok.cuneiform_tools import _CUNEIFORM_SIGNS, lookup_cuneiform_sign

print(f'Signs loaded: {len(_CUNEIFORM_SIGNS)}')

if len(_CUNEIFORM_SIGNS) > 0:
    # Test lookup
    result = lookup_cuneiform_sign('A', 'name')
    print(f"\nLookup 'A' results:")
    print(f"  Found: {result.get('found')}")
    print(f"  Matches: {result.get('count')}")
    if result.get('matches'):
        print(f"  First match: {result['matches'][0]}")
