import sys
from pathlib import Path
sys.path.insert(0, 'src')

from ancientgrok.report_tools import create_research_report

result = create_research_report(
    'Ancient Babylon Test Report',
    '''\\section{Introduction}
This document tests the report generation system.

\\section{Historical Context}
Babylon was a major ancient city.

\\section{Conclusion}
The report system works.''',
    abstract='Test abstract for report generation.'
)

import json
print(json.dumps(result, indent=2))

if result.get('success'):
    print(f"\nPDF exists: {Path(result['pdf_path']).exists()}")
    print(f"File size: {Path(result['pdf_path']).stat().st_size} bytes")
