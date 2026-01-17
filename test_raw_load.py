import sys
sys.path.insert(0, 'src')

# Force fresh import
if 'ancientgrok.cuneiform_tools' in sys.modules:
    del sys.modules['ancientgrok.cuneiform_tools']

from ancientgrok.cuneiform_tools import lookup_cuneiform_sign

# Test the tool
result = lookup_cuneiform_sign('A', 'name')

print(f"Found: {result.get('found')}")
print(f"Message: {result.get('message')}")

if result.get('database'):
    lines = result['database'].strip().split('\n')
    print(f"\nDatabase loaded: {len(lines)} lines")
    print(f"First 3 lines:")
    for line in lines[:3]:
        print(f"  {line[:80]}...")
