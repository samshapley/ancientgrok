import sys
sys.path.insert(0, 'src')
from ancientgrok.cuneiform_tools import _CUNEIFORM_SIGNS, lookup_cuneiform_sign

print(f'Signs loaded: {len(_CUNEIFORM_SIGNS)}')

if len(_CUNEIFORM_SIGNS) > 0:
    result = lookup_cuneiform_sign('A', 'name')
    print(f"Search found: {result.get('found')}")
    print(f"Match count: {result.get('count')}")
    if result.get('matches'):
        print(f"First match: {result['matches'][0]}")
else:
    print('ERROR: No signs loaded - checking path...')
    from pathlib import Path
    expected = Path('src/ancientgrok/cuneiform_tools.py').parent.parent.parent.parent / 'data' / 'unicode' / 'cuneiform_characters.txt'
    print(f'Expected path: {expected}')
    print(f'Path exists: {expected.exists()}')
