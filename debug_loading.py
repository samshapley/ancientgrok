from pathlib import Path

# Simulate the exact code from cuneiform_tools.py
file_path = Path(__file__).resolve()
print(f'This file: {file_path}')
print(f'Parent 1: {file_path.parent}')
print(f'Parent 2: {file_path.parent.parent}')
print(f'Parent 3: {file_path.parent.parent.parent}')
print(f'Parent 4: {file_path.parent.parent.parent.parent}')

data_file = file_path.parent.parent.parent.parent / "data" / "unicode" / "cuneiform_characters.txt"
print(f'\nData file path: {data_file}')
print(f'Exists: {data_file.exists()}')
print(f'Is file: {data_file.is_file()}')

if data_file.exists():
    with data_file.open('r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        print(f'\nNon-comment lines: {len(lines)}')
        if lines:
            print(f'First line: {lines[0]}')
