"""Vision tools for AncientGrok - image viewing and analysis using Grok's vision capabilities."""

import os
import base64
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional


def view_analyze_image(
    image_source: str,
    analysis_prompt: str = "Describe this image in detail",
    detail_level: str = "high"
) -> Dict[str, Any]:
    """View and analyze an image using Grok's vision capabilities.
    
    Args:
        image_source: File path or URL to image (supports local paths and URLs)
        analysis_prompt: What to analyze/look for in the image
        detail_level: "high" for detailed analysis, "low" for quick overview
    
    Returns:
        Dictionary with analysis results
    """
    try:
        from xai_sdk import Client
        from xai_sdk.chat import user, image
        
        client = Client(api_key=os.getenv("XAI_API_KEY"))
        
        # Check if it's a local file or URL
        if image_source.startswith(("http://", "https://")):
            image_url = image_source
        else:
            # Local file - convert to base64 data URL
            image_path = Path(image_source)
            if not image_path.exists():
                return {
                    "success": False,
                    "error": "File not found",
                    "message": f"Image not found at {image_source}"
                }
            
            # Read file and encode as base64
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(str(image_path))
            if mime_type is None:
                mime_type = "image/jpeg"  # Default to JPEG
            
            # Create data URL
            base64_data = base64.b64encode(image_data).decode("utf-8")
            image_url = f"data:{mime_type};base64,{base64_data}"
        
        # Create vision chat
        chat = client.chat.create(
            model="grok-4-1-fast-non-reasoning",
            store_messages=False
        )
        
        # Send image with analysis prompt
        chat.append(user(
            analysis_prompt,
            image(image_url=image_url, detail=detail_level)
        ))
        
        response = chat.sample()
        
        return {
            "success": True,
            "image_source": image_source,
            "analysis": response.content if hasattr(response, 'content') else "No analysis",
            "detail_level": detail_level,
            "message": "Image analyzed successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to analyze image: {str(e)}"
        }


# Tool schema for xai-sdk
VISION_TOOL_SCHEMAS = [
    {
        "name": "view_analyze_image",
        "description": "View and analyze images using Grok's vision capabilities. Can examine downloaded CDLI tablet images to read inscriptions, analyze generated images for accuracy, or view any accessible image file or URL. Useful for: reading cuneiform on tablet photos, verifying generated historical reconstructions, analyzing archaeological artifacts, identifying signs and symbols. Supports both local files (/tmp/cdli_images/, /tmp/ancientgrok_images/) and web URLs.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_source": {
                    "type": "string",
                    "description": "Path to image file or image URL. Examples: '/tmp/cdli_images/P000001_photo.jpg' (CDLI tablet), '/tmp/ancientgrok_images/[uuid].jpg' (generated image), 'https://cdli.earth/dl/photo/P123456.jpg' (direct CDLI URL)"
                },
                "analysis_prompt": {
                    "type": "string",
                    "description": "What to analyze or look for. Examples: 'Read and transliterate the cuneiform text on this tablet', 'Identify the signs visible in this image', 'Describe the architectural features', 'Verify historical accuracy of this reconstruction'"
                },
                "detail_level": {
                    "type": "string",
                    "enum": ["high", "low"],
                    "description": "'high' for detailed analysis (recommended for cuneiform reading), 'low' for quick overview"
                }
            },
            "required": ["image_source"]
        }
    }
]

# Function dispatcher
VISION_TOOL_FUNCTIONS = {
    "view_analyze_image": view_analyze_image
}