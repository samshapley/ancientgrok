"""Cuneiform sign reference tools for AncientGrok."""

from pathlib import Path
from typing import Dict, Any


def lookup_cuneiform_sign(
    search_term: str,
    search_type: str = "name"
) -> Dict[str, Any]:
    """Look up cuneiform sign by loading and returning the database.
    
    Args:
        search_term: What to search for
        search_type: "name", "character", or "code_point"
    
    Returns:
        Dictionary with database content
    """
    try:
        # Load the entire cuneiform database
        data_file = Path(__file__).parent / "data" / "cuneiform_characters.txt"
        
        if not data_file.exists():
            return {
                "found": False,
                "error": "Database file not found",
                "search_term": search_term,
                "message": f"Cuneiform database not accessible at {data_file}"
            }
        
        # Read raw database content
        database_text = data_file.read_text(encoding='utf-8')
        
        return {
            "found": True,
            "search_term": search_term,
            "search_type": search_type,
            "database": database_text,
            "format": "Semicolon-separated: hex_code;NAME;category;... (1,205 signs)",
            "message": f"Loaded cuneiform database for search term '{search_term}'. Parse the database to find matches."
        }
    
    except Exception as e:
        return {
            "found": False,
            "error": str(e),
            "search_term": search_term,
            "message": f"Failed to load cuneiform database: {str(e)}"
        }


def list_cuneiform_signs(
    limit: int = 50,
    offset: int = 0,
    name_filter: str = None
) -> Dict[str, Any]:
    """List cuneiform signs by loading, parsing, and filtering the database.
    
    Args:
        limit: How many to show (default: 50)
        offset: Starting position (default: 0)
        name_filter: Optional filter - only show signs where name contains this string
    
    Returns:
        Dictionary with parsed and filtered sign list
    """
    try:
        # Load the entire cuneiform database
        data_file = Path(__file__).parent / "data" / "cuneiform_characters.txt"
        
        if not data_file.exists():
            return {
                "found": False,
                "error": "Database file not found",
                "message": f"Cuneiform database not accessible at {data_file}"
            }
        
        # Parse the database
        database_text = data_file.read_text(encoding='utf-8')
        all_signs = []
        
        for line in database_text.strip().split('\n'):
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(';')
            if len(parts) >= 2:
                hex_code = parts[0]
                name = parts[1]
                
                # Apply filter if provided
                if name_filter and name_filter.upper() not in name.upper():
                    continue
                
                # Create sign entry
                try:
                    char = chr(int(hex_code, 16))
                except:
                    char = "N/A"
                
                all_signs.append({
                    "code_point": f"U+{hex_code}",
                    "name": name,
                    "character": char
                })
        
        # Apply pagination
        subset = all_signs[offset:offset + limit]
        
        return {
            "found": True,
            "signs": subset,
            "showing": len(subset),
            "offset": offset,
            "total_matching": len(all_signs),
            "total_database": 1205,
            "name_filter": name_filter,
            "message": f"Showing {len(subset)} of {len(all_signs)} signs" + (f" matching '{name_filter}'" if name_filter else "")
        }
    
    except Exception as e:
        return {
            "found": False,
            "error": str(e),
            "message": f"Failed to list cuneiform signs: {str(e)}"
        }


# Tool schemas for xai-sdk
CUNEIFORM_TOOL_SCHEMAS = [
    {
        "name": "lookup_cuneiform_sign",
        "description": "Look up cuneiform signs in the Unicode cuneiform database (1,205 signs). This tool loads the complete database and returns it for you to parse and extract matching signs. The database format is semicolon-separated: hex_code;SIGN_NAME;category;... You can search by sign name (contains match), Unicode character, or code point. Covers all Sumero-Akkadian cuneiform signs (U+12000-U+1254F).",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "What to search for. Examples: 'A' (sign name), '𒀀' (Unicode character), 'U+12000' or '12000' (code point), 'DUG' (vessel sign)"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["name", "character", "code_point"],
                    "description": "'name' to search sign names (default), 'character' for Unicode char, 'code_point' for hex code"
                }
            },
            "required": ["search_term"]
        }
    },
    {
        "name": "list_cuneiform_signs",
        "description": "Browse and filter cuneiform signs from the Unicode database (1,205 total signs). Can filter by name pattern to find specific types of signs (e.g., 'WATER', 'KING', 'A'). Returns parsed sign list with Unicode characters, names, and code points. Supports pagination.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of signs to return (default: 50, max: 200)"
                },
                "offset": {
                    "type": "integer",
                    "description": "Starting position for pagination (default: 0)"
                },
                "name_filter": {
                    "type": "string",
                    "description": "Filter signs by name pattern (case-insensitive). Examples: 'WATER' returns all signs with WATER in name, 'A' returns all A-variant signs, 'KING' finds LUGAL and variants"
                }
            }
        }
    }
]


# Function dispatcher
CUNEIFORM_TOOL_FUNCTIONS = {
    "lookup_cuneiform_sign": lookup_cuneiform_sign,
    "list_cuneiform_signs": list_cuneiform_signs
}