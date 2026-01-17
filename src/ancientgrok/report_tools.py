"""Research report generation tools for AncientGrok."""

import os
import subprocess
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def create_research_report(
    title: str,
    content: str,
    author: str = "AncientGrok Research",
    abstract: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a LaTeX research report and compile to PDF.
    
    Args:
        title: Report title
        content: Main content (LaTeX-formatted or plain text)
        author: Author name (default: "AncientGrok Research")
        abstract: Optional abstract/summary
    
    Returns:
        Dictionary with PDF path and compilation status
    """
    try:
        # Create output directory
        output_dir = Path("desktop/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
        safe_title = safe_title.replace(' ', '_')
        base_name = f"{safe_title}_{timestamp}"
        
        tex_file = output_dir / f"{base_name}.tex"
        pdf_file = output_dir / f"{base_name}.pdf"
        
        # Escape LaTeX special characters in content if it's plain text
        def escape_latex(text: str) -> str:
            """Escape LaTeX special characters."""
            replacements = {
                '\\': r'\textbackslash{}',
                '{': r'\{',
                '}': r'\}',
                '$': r'\$',
                '&': r'\&',
                '%': r'\%',
                '#': r'\#',
                '_': r'\_',
                '~': r'\textasciitilde{}',
                '^': r'\textasciicircum{}',
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            return text
        
        # Check if content already contains LaTeX commands
        is_latex = '\\section' in content or '\\subsection' in content or '\\begin{' in content
        
        if not is_latex:
            # Plain text - escape and format
            content = escape_latex(content)
            # Convert newlines to paragraphs
            content = content.replace('\n\n', '\n\n\\medskip\n\n')
        
        # Create LaTeX document
        latex_template = r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{amssymb}

\title{''' + title + r'''}
\author{''' + author + r'''}
\date{''' + datetime.now().strftime("%B %d, %Y") + r'''}

\begin{document}

\maketitle

'''
        
        if abstract:
            latex_template += r'''\begin{abstract}
''' + (escape_latex(abstract) if not is_latex else abstract) + r'''
\end{abstract}

'''
        
        latex_template += content + r'''

\end{document}
'''
        
        # Write LaTeX file
        tex_file.write_text(latex_template)
        
        # Get absolute paths
        tex_file_abs = tex_file.resolve()
        output_dir_abs = output_dir.resolve()
        
        # Compile to PDF using pdflatex with absolute paths
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', f'-output-directory={output_dir_abs}', str(tex_file_abs)],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd())  # Run from current working directory
        )
        
        # Clean up auxiliary files
        for ext in ['.aux', '.log', '.out']:
            aux_file = output_dir / f"{base_name}{ext}"
            if aux_file.exists():
                aux_file.unlink()
        
        if pdf_file.exists():
            # Auto-open the PDF
            import platform
            
            try:
                if platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", str(pdf_file)])
                else:  # Linux
                    subprocess.Popen(["xdg-open", str(pdf_file)])
            except Exception as e:
                # Non-critical failure - PDF still generated
                pass
            
            return {
                "success": True,
                "pdf_path": str(pdf_file),
                "tex_path": str(tex_file),
                "title": title,
                "pages": "Unknown",  # Could parse PDF for page count
                "message": f"Research report compiled successfully to {pdf_file}"
            }
        else:
            return {
                "success": False,
                "error": "PDF compilation failed",
                "tex_path": str(tex_file),
                "latex_output": result.stdout[-500:] if result.stdout else "",
                "message": "LaTeX compilation failed. Check .tex file for errors."
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create research report: {str(e)}"
        }


# Tool schema for xai-sdk
REPORT_TOOL_SCHEMA = {
    "name": "create_research_report",
    "description": "Generate a formatted LaTeX research report from your research and compile it to PDF. Use this when you've conducted substantial research (using web_search, CDLI tools, etc.) and want to create a professional document summarizing findings. The report is automatically formatted with proper sections, saved to desktop/reports/, and can be opened for viewing. Perfect for: literature reviews, archaeological site summaries, linguistic analyses, chronological studies, artifact catalogs, scholarly syntheses.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Title of the research report. Examples: 'Ur III Administrative Texts from Girsu: A Survey', 'Hammurabi's Code: Recent Scholarship and Interpretation', 'The Development of Cuneiform Writing Systems'"
            },
            "content": {
                "type": "string",
                "description": "Main content of the report. Can be LaTeX-formatted (with \\section{}, \\subsection{}, etc.) or plain text (will be auto-formatted). Include your research findings, analysis, citations, and conclusions. Structure recommendations: Introduction, Methodology, Findings, Discussion, Conclusion, References."
            },
            "author": {
                "type": "string",
                "description": "Author name (default: 'AncientGrok Research'). Can customize for specific projects or collaborations."
            },
            "abstract": {
                "type": "string",
                "description": "Optional abstract/summary (150-250 words). Brief overview of research question, methods, and key findings."
            }
        },
        "required": ["title", "content"]
    }
}

REPORT_TOOL_SCHEMAS = [REPORT_TOOL_SCHEMA]

REPORT_TOOL_FUNCTIONS = {
    "create_research_report": create_research_report
}