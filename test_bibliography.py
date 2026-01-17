import sys
sys.path.insert(0, 'src')

from ancientgrok.bibliography_tools import get_cdli_bibliography, download_paper

# Test 1: CDLI bibliography
print('Test 1: CDLI Bibliography')
print('='*50)
result = get_cdli_bibliography('P000001', 'tablet', 'bibtex')
print(f"Success: {result.get('success')}")
if result.get('file_path'):
    print(f"Saved to: {result['file_path']}")
if result.get('content'):
    print(f"Content preview: {result['content'][:200]}...")
print()

# Test 2: Paper download (using a test PDF)
print('Test 2: Paper Download')
print('='*50)
test_pdf_url = 'https://arxiv.org/pdf/2109.04513'  # Akkadian NMT paper
result2 = download_paper(test_pdf_url, 'akkadian_nmt_test.pdf')
print(f"Success: {result2.get('success')}")
if result2.get('file_path'):
    print(f"Downloaded to: {result2['file_path']}")
    print(f"Size: {result2.get('file_size', 0) / 1024:.1f} KB")
