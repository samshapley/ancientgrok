from pathlib import Path

# Direct test - load the file directly without importing the module
data_file = Path('src/ancientgrok/data/cuneiform_characters.txt')
print(f'Data file: {data_file.resolve()}')
print(f'Exists: {data_file.exists()}')

if data_file.exists():
    signs = {}
    with data_file.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                signs[parts[0]] = {'code_point': parts[0], 'name': parts[1]}
    
    print(f'\nSigns loaded: {len(signs)}')
    
    # Test search
    matches = [s for cp, s in signs.items() if 'A' in s['name']]
    print(f'Signs with "A" in name: {len(matches)}')
    if matches:
        print(f'First 3: {matches[:3]}')
