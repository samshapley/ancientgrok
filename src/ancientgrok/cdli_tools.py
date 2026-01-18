"""CDLI tools for AncientGrok - client-side tools for cuneiform database access."""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add cdli-cli to Python path (bundled in ancientgrok/cdli-cli/)
cdli_path = Path(__file__).parent.parent.parent / "cdli-cli" / "src"
if str(cdli_path) not in sys.path:
    sys.path.insert(0, str(cdli_path))

from cdli_cli.client import CDLIClient


def search_cdli(query: str, per_page: int = 10) -> Dict[str, Any]:
    """Search CDLI database for cuneiform tablets.
    
    Args:
        query: Search query (e.g., "Ur III", "administrative", "Girsu")
        per_page: Number of results to return (default: 10, max: 100)
    
    Returns:
        Dictionary with search results
    """
    try:
        with CDLIClient() as client:
            results = client.search(query, per_page=min(per_page, 100))
            
            # Format for agent consumption
            tablets = []
            for tablet in results.results[:per_page]:
                tablets.append({
                    "id": tablet.get("id"),
                    "designation": tablet.get("designation", "N/A"),
                    "museum_no": tablet.get("museum_no", "N/A"),
                    "period": tablet.get("period", {}).get("period", "N/A") if isinstance(tablet.get("period"), dict) else str(tablet.get("period", "N/A")),
                    "provenance": tablet.get("provenance", "N/A"),
                    "genre": tablet.get("genre", "N/A"),
                })
            
            return {
                "total_found": results.total,
                "showing": len(tablets),
                "tablets": tablets
            }
    except Exception as e:
        return {
            "error": str(e),
            "total_found": 0,
            "showing": 0,
            "tablets": []
        }


def get_tablet_details(tablet_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific tablet.
    
    Args:
        tablet_id: Tablet P-number (e.g., "P000001")
    
    Returns:
        Dictionary with tablet metadata
    """
    try:
        with CDLIClient() as client:
            tablet = client.get_tablet(tablet_id)
            
            if isinstance(tablet, dict):
                # Extract key fields for agent
                return {
                    "id": tablet.get("id"),
                    "designation": tablet.get("designation"),
                    "museum_no": tablet.get("museum_no"),
                    "excavation_no": tablet.get("excavation_no"),
                    "period": tablet.get("period", {}).get("period") if isinstance(tablet.get("period"), dict) else str(tablet.get("period")),
                    "provenance": tablet.get("provenance"),
                    "genre": tablet.get("genre"),
                    "language": tablet.get("language"),
                    "dimensions": {
                        "height": tablet.get("height"),
                        "width": tablet.get("width"),
                        "thickness": tablet.get("thickness")
                    },
                    "has_inscription": bool(tablet.get("inscription")),
                    "cdli_url": f"https://cdli.earth/{tablet_id}"
                }
            else:
                return {"error": "Tablet data not in expected format"}
    except Exception as e:
        return {"error": str(e)}


def download_tablet_image(tablet_id: str, image_type: str = "photo") -> Dict[str, Any]:
    """Download image of a cuneiform tablet.
    
    Args:
        tablet_id: Tablet P-number (e.g., "P000001")
        image_type: "photo" or "lineart" (default: "photo")
    
    Returns:
        Dictionary with download result
    """
    try:
        with CDLIClient() as client:
            # Ensure P prefix
            if not tablet_id.startswith("P"):
                tablet_id = f"P{tablet_id}"
            
            output_path = Path(f"/tmp/cdli_images/{tablet_id}_{image_type}.jpg")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            result_path = client.download_image(
                tablet_id,
                image_type=image_type,
                output_path=output_path
            )
            
            # Auto-open the image
            import subprocess
            import platform
            try:
                if platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", str(result_path)])
                elif platform.system() == "Linux":
                    subprocess.Popen(["xdg-open", str(result_path)])
                # Windows: subprocess.Popen(["start", str(result_path)], shell=True)
            except Exception:
                pass  # Don't fail if auto-open doesn't work
            
            return {
                "success": True,
                "tablet_id": tablet_id,
                "image_type": image_type,
                "file_path": str(result_path),
                "cdli_url": client.get_image_url(tablet_id, image_type),
                "message": f"Downloaded {image_type} of {tablet_id} to {result_path} (auto-opened)"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to download {image_type} for {tablet_id}"
        }


def list_periods() -> Dict[str, Any]:
    """List all historical periods in CDLI database.
    
    Returns:
        Dictionary with periods list
    """
    try:
        with CDLIClient() as client:
            results = client.list_periods(per_page=50)
            
            periods = []
            for period in results.results:
                if isinstance(period, dict):
                    periods.append(period.get("period", str(period)))
                else:
                    periods.append(str(period))
            
            return {
                "total": results.total,
                "periods": periods[:30]  # First 30 for brevity
            }
    except Exception as e:
        return {"error": str(e), "periods": []}


def list_collections() -> Dict[str, Any]:
    """List museums and collections holding cuneiform artifacts.
    
    Returns:
        Dictionary with collections list
    """
    try:
        with CDLIClient() as client:
            results = client.list_collections(per_page=25)
            
            collections = []
            for coll in results.results:
                if isinstance(coll, dict):
                    collections.append({
                        "name": coll.get("name", "N/A"),
                        "abbreviation": coll.get("abbreviation", ""),
                        "city": coll.get("city", ""),
                        "country": coll.get("country", "")
                    })
            
            return {
                "total": results.total,
                "showing": len(collections),
                "collections": collections
            }
    except Exception as e:
        return {"error": str(e), "collections": []}


# Tool schemas for xai-sdk
CDLI_TOOL_SCHEMAS = [
    {
        "name": "search_cdli",
        "description": "Search the Cuneiform Digital Library Initiative database for ancient tablets. Use this to find specific tablets by period, provenance, genre, or keyword. Returns tablet metadata including museum numbers, periods, and provenances.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. Can be period (e.g., 'Ur III'), location (e.g., 'Girsu'), genre (e.g., 'administrative'), or keyword."
                },
                "per_page": {
                    "type": "integer",
                    "description": "Number of results to return (1-100, default: 10)",
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_tablet_details",
        "description": "Get detailed metadata for a specific cuneiform tablet by its P-number. Returns full information including dimensions, museum location, period, provenance, genre, language, and whether inscription is available.",
        "parameters": {
            "type": "object",
            "properties": {
                "tablet_id": {
                    "type": "string",
                    "description": "Tablet P-number (e.g., 'P000001', 'P123456')"
                }
            },
            "required": ["tablet_id"]
        }
    },
    {
        "name": "download_tablet_image",
        "description": "Download a high-resolution photograph or line-art tracing of a cuneiform tablet. Saves to /tmp/cdli_images/, auto-opens in image viewer, and returns the file path and CDLI URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "tablet_id": {
                    "type": "string",
                    "description": "Tablet P-number (e.g., 'P000001')"
                },
                "image_type": {
                    "type": "string",
                    "enum": ["photo", "lineart"],
                    "description": "Type of image: 'photo' for photograph, 'lineart' for scholarly line drawing"
                }
            },
            "required": ["tablet_id"]
        }
    },
    {
        "name": "list_periods",
        "description": "List all historical periods represented in the CDLI database (e.g., Ur III, Old Babylonian, Neo-Assyrian). Useful for understanding chronology and available corpora.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "list_collections",
        "description": "List museums and institutions holding cuneiform artifacts in CDLI. Returns collection names, locations, and abbreviations.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]


# Function dispatcher for tool execution
CDLI_TOOL_FUNCTIONS = {
    "search_cdli": search_cdli,
    "get_tablet_details": get_tablet_details,
    "download_tablet_image": download_tablet_image,
    "list_periods": list_periods,
    "list_collections": list_collections
}