"""Image generation tools for AncientGrok using Grok's image generation API."""

import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from xai_sdk import Client


def generate_image(
    prompt: str,
    size: str = "1024x1024",
    n: int = 1
) -> Dict[str, Any]:
    """Generate an image using Grok's image generation API.
    
    Args:
        prompt: Description of image to generate
        size: Image dimensions (note: xAI doesn't support custom sizes yet, parameter kept for future)
        n: Number of images (1-10)
    
    Returns:
        Dictionary with image paths, URLs, and metadata
    """
    try:
        client = Client(api_key=os.getenv("XAI_API_KEY"))
        
        # Generate image using xai-sdk
        # Note: image_format can be "url" or "base64"
        response = client.image.sample(
            model="grok-imagine-image-a1",  # New unreleased model
            prompt=prompt,
            image_format="url"  # Get URL to download
        )
        
        # Download image from URL
        import httpx
        import subprocess
        import platform
        
        output_dir = Path("/tmp/ancientgrok_images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        image_response = httpx.get(response.url)
        image_response.raise_for_status()
        
        # Save to file
        output_path = output_dir / f"{uuid.uuid4().hex[:8]}.jpg"
        output_path.write_bytes(image_response.content)
        
        # Auto-open the image
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", str(output_path)])
            else:  # Linux
                subprocess.Popen(["xdg-open", str(output_path)])
        except Exception as e:
            # Non-critical failure - image still generated
            pass
        
        return {
            "success": True,
            "file_path": str(output_path),
            "image_url": response.url,
            "prompt": prompt,
            "revised_prompt": getattr(response, 'revised_prompt', None),
            "message": f"Image generated and saved to {output_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate image: {str(e)}"
        }


# Tool schema for xai-sdk (client-side tool)
IMAGE_GENERATION_TOOL_SCHEMA = {
    "name": "generate_image",
    "description": "Generate educational visualizations, historical reconstructions, or artistic renderings related to ancient civilizations. Use this to create images of: archaeological sites, artifact reconstructions, historical scenes, ancient city maps, timelines, cuneiform tablet diagrams, architectural plans, battle formations, trade routes, deity depictions, etc. Images are saved to /tmp/ancientgrok_images/ and accessible on the system.",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed description of the image to generate. Be specific about historical period, artistic style, content, and perspective. Examples: 'Photorealistic reconstruction of the Ishtar Gate in ancient Babylon with blue glazed bricks and golden lions, daytime lighting', 'Educational diagram showing the evolution of cuneiform signs from pictographs to abstract wedge-shaped marks, labeled and color-coded', 'Aerial view map of Mesopotamian city-states during the Ur III period, showing Ur, Uruk, Lagash, Nippur with rivers and trade routes'"
            },
            "n": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Number of images to generate (1-10, default: 1). Generate multiple for variations or different perspectives of the same scene"
            }
        },
        "required": ["prompt"]
    }
}

IMAGE_GENERATION_TOOL_SCHEMAS = [IMAGE_GENERATION_TOOL_SCHEMA]

IMAGE_GENERATION_FUNCTIONS = {
    "generate_image": generate_image
}