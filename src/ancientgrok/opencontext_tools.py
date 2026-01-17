"""Open Context tools for AncientGrok - archaeological database access."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .open_context_api import OpenContextAPI


def search_open_context(
    query: str,
    category: str = None,
    provenance: str = None,
    period: str = None,
    max_results: int = 25
) -> Dict[str, Any]:
    """Search Open Context archaeological database.
    
    Args:
        query: Search query (keywords, site names, artifact types)
        category: Category filter (e.g., "Bone", "Ceramic", "Architecture")
        provenance: Site/provenance filter
        period: Time period filter
        max_results: Maximum results to return (default: 25)
    
    Returns:
        Dictionary with search results
    """
    try:
        api = OpenContextAPI()
        
        # Build search URL
        base_url = "https://opencontext.org/search/"
        params = []
        
        if query:
            params.append(f"q={query}")
        if category:
            params.append(f"cat={category}")
        if provenance:
            params.append(f"prop=oc-gen-cat-loc-provenance&val={provenance}")
        if period:
            params.append(f"prop=oc-gen-cat-period&val={period}")
        
        search_url = base_url + "?" + "&".join(params) if params else base_url
        
        # Get records (limit to requested max)
        records = api.get_paged_json_records(
            search_url,
            attribute_slugs=[],
            do_paging=False  # Just get first page
        )
        
        if not records:
            return {
                "total_found": 0,
                "showing": 0,
                "results": [],
                "message": "No results found"
            }
        
        # Format for display
        formatted_results = []
        for record in records[:max_results]:
            formatted_results.append({
                "uri": record.get("uri", "N/A"),
                "label": record.get("label", "N/A"),
                "category": record.get("item category", "N/A"),
                "project": record.get("project label", "N/A"),
                "context": record.get("context label", "N/A"),
                "period": record.get("early bce/ce", "N/A"),
            })
        
        return {
            "total_found": len(records),
            "showing": len(formatted_results),
            "results": formatted_results,
            "search_url": search_url
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "total_found": 0,
            "showing": 0,
            "results": []
        }


def get_opencontext_attributes(
    url: str,
    attribute_type: str = "standard"
) -> Dict[str, Any]:
    """Get available attributes for Open Context records.
    
    Args:
        url: Open Context search URL
        attribute_type: "standard" for standardized attributes, "common" for frequently used
    
    Returns:
        Dictionary with attribute list
    """
    try:
        api = OpenContextAPI()
        
        if attribute_type == "standard":
            attributes = api.get_standard_attributes(
                url,
                add_von_den_driesch_bone_measures=True
            )
        else:  # common
            attributes = api.get_common_attributes(url, min_portion=0.2)
        
        if not attributes:
            return {
                "attributes": [],
                "count": 0,
                "message": "No attributes found"
            }
        
        # Format as list of dicts
        formatted = [
            {"slug": slug, "label": label}
            for slug, label in attributes
        ]
        
        return {
            "attributes": formatted,
            "count": len(formatted),
            "attribute_type": attribute_type
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "attributes": [],
            "count": 0
        }


def get_detailed_opencontext_records(
    url: str,
    max_records: int = 10,
    include_attributes: List[str] = None
) -> Dict[str, Any]:
    """Get detailed artifact records from Open Context with full attribute data.
    
    Args:
        url: Open Context search URL
        max_records: Maximum records to return (default: 10)
        include_attributes: Optional list of attribute slugs to include
    
    Returns:
        Dictionary with detailed record data
    """
    try:
        api = OpenContextAPI()
        
        # Get records with full attribute data
        attribute_slugs = include_attributes or []
        records = api.get_paged_json_records(
            url,
            attribute_slugs,
            do_paging=False  # Just first page for now
        )
        
        if not records:
            return {
                "found": False,
                "records": [],
                "count": 0,
                "message": "No detailed records found"
            }
        
        # Limit to requested max
        limited_records = records[:max_records]
        
        return {
            "found": True,
            "records": limited_records,
            "count": len(limited_records),
            "total_available": len(records),
            "url": url,
            "message": f"Retrieved {len(limited_records)} detailed records"
        }
    
    except Exception as e:
        return {
            "found": False,
            "error": str(e),
            "records": [],
            "count": 0
        }


# Tool schemas for xai-sdk
OPENCONTEXT_TOOL_SCHEMAS = [
    {
        "name": "search_open_context",
        "description": "Search the Open Context archaeological database for excavation records, artifacts, ecofacts, and field observations from archaeological projects worldwide. Returns data on bones, ceramics, architecture, burials, and other archaeological materials. Useful for comparative studies beyond just cuneiform texts.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. Can include keywords, site names, artifact types, animal species, etc. Examples: 'cattle bones', 'ceramic vessels', 'Çatalhöyük', 'obsidian tools'"
                },
                "category": {
                    "type": "string",
                    "description": "Category filter for item types. Examples: 'oc-gen-cat-bio-subj-ecofact' for animal bones, 'oc-gen-cat-arch-element' for architecture, 'oc-gen-cat-object' for artifacts"
                },
                "provenance": {
                    "type": "string",
                    "description": "Archaeological site or provenance. Examples: 'Çatalhöyük', 'Domuztepe', 'Petra'"
                },
                "period": {
                    "type": "string",
                    "description": "Time period. Examples: 'Neolithic', 'Bronze Age', 'Iron Age', 'Roman'"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 25, max: 100)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_opencontext_attributes",
        "description": "Get available descriptive attributes for Open Context records. Returns standardized attributes (like taxonomic IDs, anatomical IDs) or commonly used project-specific attributes. Useful for understanding what data fields are available for analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Open Context search URL to analyze for attributes"
                },
                "attribute_type": {
                    "type": "string",
                    "enum": ["standard", "common"],
                    "description": "'standard' for widely-used standardized attributes (taxonomies, measurements), 'common' for frequently used project-specific attributes"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_detailed_opencontext_records",
        "description": "Get detailed artifact records from Open Context with complete attribute data including measurements, classifications, taxonomic IDs, contexts. Returns richer data than basic search. Useful for in-depth analysis of specific artifacts, getting measurement data for bones, detailed ceramic descriptions, architectural feature data, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Open Context search URL from previous search_open_context results"
                },
                "max_records": {
                    "type": "integer",
                    "description": "Maximum records to retrieve (default: 10, max: 50 for performance)"
                },
                "include_attributes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional: Specific attribute slugs to include (e.g., ['oc-zoo-has-anat-id', 'obo-foodon-00001303'])"
                }
            },
            "required": ["url"]
        }
    }
]


# Function dispatcher for tool execution
OPENCONTEXT_TOOL_FUNCTIONS = {
    "search_open_context": search_open_context,
    "get_opencontext_attributes": get_opencontext_attributes,
    "get_detailed_opencontext_records": get_detailed_opencontext_records
}