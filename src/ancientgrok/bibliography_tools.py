"""Bibliography and paper download tools for AncientGrok."""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib

# Add cdli-cli to Python path (bundled in ancientgrok/cdli-cli/)
cdli_path = Path(__file__).parent.parent.parent / "cdli-cli" / "src"
if str(cdli_path) not in sys.path:
    sys.path.insert(0, str(cdli_path))

from cdli_cli.client import CDLIClient
from cdli_cli.models import BibliographyFormat
import httpx


def get_cdli_bibliography(
    item_id: str,
    item_type: str = "tablet",
    format: str = "bibtex"
) -> Dict[str, Any]:
    """Get bibliography for a CDLI item (tablet or publication).
    
    Args:
        item_id: ID of the item (P-number for tablets, numeric ID for publications)
        item_type: "tablet" or "publication"
        format: "bibtex", "ris", "csljson", or "formatted"
    
    Returns:
        Dictionary with bibliography data
    """
    try:
        # Map format string to enum
        format_map = {
            "bibtex": BibliographyFormat.BIBTEX,
            "ris": BibliographyFormat.RIS,
            "csljson": BibliographyFormat.CSLJSON,
            "formatted": BibliographyFormat.FORMATTED
        }
        
        bib_format = format_map.get(format, BibliographyFormat.BIBTEX)
        
        with CDLIClient() as client:
            if item_type == "tablet":
                bibliography = client.get_tablet_bibliography(item_id, bib_format)
            else:  # publication
                bibliography = client.get_publication_bibliography(item_id, bib_format)
            
            # Save to file
            output_dir = Path("desktop/bibliographies")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            ext = {
                "bibtex": ".bib",
                "ris": ".ris",
                "csljson": ".json",
                "formatted": ".txt"
            }.get(format, ".bib")
            
            output_file = output_dir / f"{item_id}_bibliography{ext}"
            output_file.write_text(bibliography)
            
            return {
                "success": True,
                "item_id": item_id,
                "item_type": item_type,
                "format": format,
                "file_path": str(output_file),
                "content": bibliography,
                "message": f"Bibliography exported to {output_file}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get bibliography for {item_id}: {str(e)}"
        }


def download_paper(
    url: str,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """Download an academic paper PDF from a URL.
    
    Args:
        url: URL of the PDF to download
        filename: Optional custom filename (default: generated from URL hash)
    
    Returns:
        Dictionary with download result
    """
    try:
        # Create output directory
        output_dir = Path("desktop/papers")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            # Use hash of URL to create unique filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"paper_{url_hash}.pdf"
        
        # Ensure .pdf extension
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        output_path = output_dir / filename
        
        # Download the PDF
        response = httpx.get(url, timeout=120.0, follow_redirects=True)
        response.raise_for_status()
        
        # Verify it's actually a PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower() and not url.lower().endswith('.pdf'):
            return {
                "success": False,
                "error": "URL does not appear to be a PDF",
                "content_type": content_type,
                "message": f"URL returned {content_type}, not a PDF"
            }
        
        # Save the PDF
        output_path.write_bytes(response.content)
        
        # Auto-open the PDF
        import subprocess
        import platform
        
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", str(output_path)])
            else:  # Linux
                subprocess.Popen(["xdg-open", str(output_path)])
        except Exception:
            pass  # Non-critical
        
        return {
            "success": True,
            "url": url,
            "file_path": str(output_path),
            "file_size": len(response.content),
            "message": f"Paper downloaded to {output_path} ({len(response.content) / 1024:.1f} KB)"
        }
    
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}",
            "url": url,
            "message": f"Failed to download (HTTP {e.response.status_code})"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "message": f"Failed to download paper: {str(e)}"
        }


# Tool schemas for xai-sdk - Only include working tools
BIBLIOGRAPHY_TOOL_SCHEMAS = [
    {
        "name": "download_paper",
        "description": "Download academic papers (PDFs) from URLs. Use this after finding papers via web_search to download and save them for reference. Saves to desktop/papers/ and auto-opens. Works with direct PDF URLs from arXiv, JSTOR, ResearchGate, institutional repositories, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Direct URL to PDF file. Examples: 'https://arxiv.org/pdf/1234.5678.pdf', 'https://cdli.ucla.edu/pubs/paper.pdf', 'https://university.edu/~scholar/paper.pdf'"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional custom filename (default: auto-generated from URL). Should be descriptive, e.g., 'gutherz_2023_akkadian_nmt.pdf'"
                }
            },
            "required": ["url"]
        }
    }
]


# Function dispatcher - Only include working function
BIBLIOGRAPHY_TOOL_FUNCTIONS = {
    "download_paper": download_paper
}