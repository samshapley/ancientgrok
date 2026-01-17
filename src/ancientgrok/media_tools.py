"""Advanced media tools for AncientGrok - video generation/editing and image editing."""

import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

import httpx


def generate_video(
    prompt: str,
    duration: Optional[int] = None,
    model: str = "grok-imagine-video-v2"
) -> Dict[str, Any]:
    """Generate a video using Grok's video generation API.
    
    Args:
        prompt: Description of video to generate
        duration: Video duration in seconds (if supported)
        model: Video generation model (default: grok-imagine-video-v2)
    
    Returns:
        Dictionary with request ID and status (async generation)
    """
    try:
        api_key = os.getenv("XAI_API_KEY")
        
        # Video generation is asynchronous - submit request
        response = httpx.post(
            "https://api.x.ai/v1/videos/generations",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "prompt": prompt,
                "model": model
            },
            timeout=60.0
        )
        response.raise_for_status()
        
        result = response.json()
        request_id = result.get("request_id")
        
        if not request_id:
            return {
                "success": False,
                "error": "No request ID returned",
                "message": "Video generation request failed"
            }
        
        # Poll for completion
        max_wait = 300  # 5 minutes
        poll_interval = 10
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            status_response = httpx.get(
                f"https://api.x.ai/v1/videos/{request_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30.0
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            
            state = status_data.get("status", "")
            
            if state == "completed":
                video_url = status_data.get("url")
                
                # Download video
                output_dir = Path("/tmp/ancientgrok_videos")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                video_data = httpx.get(video_url, timeout=120.0)
                video_data.raise_for_status()
                
                output_path = output_dir / f"{uuid.uuid4().hex[:8]}.mp4"
                output_path.write_bytes(video_data.content)
                
                # Auto-open the video
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
                    "file_path": str(output_path),
                    "video_url": video_url,
                    "prompt": prompt,
                    "request_id": request_id,
                    "message": f"Video generated and saved to {output_path}"
                }
            
            elif state in ["failed", "error"]:
                return {
                    "success": False,
                    "error": status_data.get("error", "Unknown error"),
                    "request_id": request_id,
                    "message": "Video generation failed"
                }
        
        # Timeout
        return {
            "success": False,
            "error": "Timeout waiting for video",
            "request_id": request_id,
            "message": f"Video generation timed out after {max_wait}s"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate video: {str(e)}"
        }


def edit_video(
    video_url: str,
    edit_prompt: str,
    model: str = "grok-imagine-video-v2"
) -> Dict[str, Any]:
    """Edit a video using Grok's video editing API.
    
    Args:
        video_url: URL of existing video to edit
        edit_prompt: Description of edits to make
        model: Video editing model (default: grok-imagine-video-v2)
    
    Returns:
        Dictionary with edited video path and metadata
    """
    try:
        api_key = os.getenv("XAI_API_KEY")
        
        # Submit video edit request
        response = httpx.post(
            "https://api.x.ai/v1/videos/edits",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "prompt": edit_prompt,
                "video": {"url": video_url}
            },
            timeout=60.0
        )
        response.raise_for_status()
        
        result = response.json()
        request_id = result.get("request_id")
        
        # Poll for completion (similar to generate_video)
        max_wait = 300
        poll_interval = 10
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            status_response = httpx.get(
                f"https://api.x.ai/v1/videos/{request_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30.0
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            
            if status_data.get("status") == "completed":
                edited_url = status_data.get("url")
                
                # Download edited video
                output_dir = Path("/tmp/ancientgrok_videos")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                video_data = httpx.get(edited_url, timeout=120.0)
                video_data.raise_for_status()
                
                output_path = output_dir / f"edited_{uuid.uuid4().hex[:8]}.mp4"
                output_path.write_bytes(video_data.content)
                
                # Auto-open the edited video
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
                    "file_path": str(output_path),
                    "video_url": edited_url,
                    "edit_prompt": edit_prompt,
                    "original_url": video_url,
                    "message": f"Edited video saved to {output_path}"
                }
            
            elif status_data.get("status") in ["failed", "error"]:
                return {
                    "success": False,
                    "error": status_data.get("error", "Unknown error"),
                    "message": "Video editing failed"
                }
        
        return {
            "success": False,
            "error": "Timeout",
            "message": f"Video editing timed out after {max_wait}s"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to edit video: {str(e)}"
        }


def edit_image(
    image_url: str,
    edit_prompt: str,
    model: str = "grok-imagine-image-a1"
) -> Dict[str, Any]:
    """Edit an image using Grok's image editing API.
    
    Args:
        image_url: URL of existing image to edit (or base64 data URL)
        edit_prompt: Description of edits to make
        model: Image editing model
    
    Returns:
        Dictionary with edited image path and metadata
    """
    try:
        api_key = os.getenv("XAI_API_KEY")
        
        # Submit image edit request
        response = httpx.post(
            "https://api.x.ai/v1/images/edits",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "prompt": edit_prompt,
                "image": {"url": image_url},
                "model": model
            },
            timeout=60.0
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Image editing appears to be synchronous (returns data directly)
        if "data" in result and len(result["data"]) > 0:
            edited_url = result["data"][0].get("url")
            
            if edited_url:
                # Download edited image
                output_dir = Path("/tmp/ancientgrok_images")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                image_data = httpx.get(edited_url, timeout=60.0)
                image_data.raise_for_status()
                
                output_path = output_dir / f"edited_{uuid.uuid4().hex[:8]}.jpg"
                output_path.write_bytes(image_data.content)
                
                # Auto-open the edited image
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
                    "file_path": str(output_path),
                    "image_url": edited_url,
                    "edit_prompt": edit_prompt,
                    "original_url": image_url,
                    "message": f"Edited image saved to {output_path}"
                }
        
        return {
            "success": False,
            "error": "No edited image returned",
            "message": "Image editing failed"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to edit image: {str(e)}"
        }


# Tool schemas for xai-sdk
MEDIA_TOOL_SCHEMAS = [
    {
        "name": "generate_video",
        "description": "Generate educational videos, historical reconstructions, or animated visualizations related to ancient civilizations. Use this to create: time-lapse views of archaeological sites, animated maps showing empire expansion, demonstrations of ancient crafts, reconstructions of historical events, visual timelines, etc. Videos are saved to /tmp/ancientgrok_videos/. Note: Video generation is asynchronous and may take 1-5 minutes.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed description of the video to generate. Be specific about content, motion, camera angles, lighting, historical accuracy. Examples: 'Time-lapse of the construction of the Hanging Gardens of Babylon from foundation to completion', 'Animated map showing the expansion of the Assyrian Empire from 900-600 BCE with territory coloring by period', 'Demonstration of ancient Sumerian cuneiform writing technique with stylus on wet clay'"
                },
                "duration": {
                    "type": "integer",
                    "description": "Desired video duration in seconds (if supported by model)"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "edit_video",
        "description": "Edit existing videos to add effects, change scenes, or modify content. Useful for refining generated videos or adding historical context to existing footage. Videos are saved to /tmp/ancientgrok_videos/",
        "parameters": {
            "type": "object",
            "properties": {
                "video_url": {
                    "type": "string",
                    "description": "URL of the video to edit (from previous generation or external source)"
                },
                "edit_prompt": {
                    "type": "string",
                    "description": "Description of edits to apply. Examples: 'Add ancient Mesopotamian architectural details', 'Change time of day to sunset', 'Add historical figures in period-appropriate clothing'"
                }
            },
            "required": ["video_url", "edit_prompt"]
        }
    },
    {
        "name": "edit_image",
        "description": "Edit existing images to add details, change elements, or enhance content. Useful for refining generated images, adding archaeological context, or modifying historical reconstructions. Edited images are saved to /tmp/ancientgrok_images/",
        "parameters": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL or data URL of image to edit. Can be from previous generation, CDLI tablet image, or external source. Supports data URLs like 'data:image/png;base64,...'"
                },
                "edit_prompt": {
                    "type": "string",
                    "description": "Description of edits to apply. Examples: 'Add cuneiform inscriptions to the tablet', 'Restore damaged portions of the artifact', 'Add historical context labels', 'Enhance weathered stone details'"
                }
            },
            "required": ["image_url", "edit_prompt"]
        }
    }
]

MEDIA_TOOL_FUNCTIONS = {
    "generate_video": generate_video,
    "edit_video": edit_video,
    "edit_image": edit_image
}