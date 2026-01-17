"""Google Gemini client with structured outputs and batch support."""

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google import genai

from ..unified.base import BaseTranslationClient
from ..unified.tools import TranslationTool


class GeminiClient(BaseTranslationClient):
    """Google Gemini client with structured outputs and proper batch API support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3-pro-preview"):
        self.client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model = model
        
        # Define response schema for structured outputs
        self.response_schema = {
            "type": "object",
            "properties": {
                "translation": {"type": "string", "description": "The English translation"},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"], "description": "Confidence level"},
                "notes": {"type": "string", "description": "Optional notes about translation"}
            },
            "required": ["translation", "confidence"]
        }
        
        # Configure safety settings to allow academic/historical content
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
    def translate(
        self,
        sumerian_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Translate single text using Gemini structured outputs.
        
        Args:
            sumerian_text: Text to translate
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
            monolingual_base: Optional monolingual sentences (not yet implemented)
            prompt_builder: Optional ModularPromptBuilder (not yet implemented)
        """
        user_prompt = self._build_user_prompt(sumerian_text, few_shot_examples)
        sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT
        full_prompt = sys_prompt + "\n\n" + user_prompt + "\n\nProvide a JSON response with translation, confidence (high/medium/low), and notes."
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config={
                    "temperature": 1.0,
                    "max_output_tokens": 1024,
                    "response_mime_type": "application/json",
                    "response_schema": self.response_schema,
                    "safety_settings": self.safety_settings
                }
            )
            
            # Check for blocks
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else None
                return {
                    "translation": "",
                    "confidence": "error",
                    "notes": f"Gemini blocked response (finish_reason: {finish_reason})",
                    "model": self.model,
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                }
            
            # Parse JSON
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError as e:
                return {
                    "translation": "",
                    "confidence": "error",
                    "notes": f"JSON parse error: {str(e)} | Raw: {response.text[:100]}",
                    "model": self.model,
                    "usage": {
                        "input_tokens": response.usage_metadata.prompt_token_count,
                        "output_tokens": response.usage_metadata.candidates_token_count
                    }
                }
            
            return {
                "translation": result.get("translation", ""),
                "confidence": result.get("confidence", "medium"),
                "notes": result.get("notes", ""),
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage_metadata.prompt_token_count,
                    "output_tokens": response.usage_metadata.candidates_token_count
                }
            }
            
        except Exception as e:
            return {
                "translation": "",
                "confidence": "error",
                "notes": f"Gemini API error: {str(e)}",
                "model": self.model,
                "usage": {"input_tokens": 0, "output_tokens": 0}
            }
    
    def translate_batch(
        self,
        sumerian_texts: List[str],
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None,
        poll_interval: float = 60.0,
        timeout: float = 7200.0
    ) -> List[Dict[str, Any]]:
        """Translate batch using Gemini Batch API (50% savings, 24h SLO).
        
        Args:
            sumerian_texts: List of texts
            few_shot_examples: Optional examples  
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
            monolingual_base: Optional monolingual sentences (not yet implemented)
            prompt_builder: Optional ModularPromptBuilder (not yet implemented)
            poll_interval: Polling interval
            timeout: Max wait time
        """
        batch_file_path = Path(f"/tmp/gemini_batch_{uuid.uuid4().hex[:8]}.jsonl")
        sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT
        
        with open(batch_file_path, 'w') as f:
            for i, sumerian_text in enumerate(sumerian_texts):
                user_prompt = self._build_user_prompt(sumerian_text, few_shot_examples)
                full_prompt = sys_prompt + "\n\n" + user_prompt + "\n\nProvide a JSON response with translation, confidence (high/medium/low), and notes. Return ONLY valid JSON."
                
                request = {
                    "key": f"trans_{i}",
                    "request": {
                        "contents": [{"parts": [{"text": full_prompt}]}],
                        "generationConfig": {
                            "temperature": 1.0,
                            "maxOutputTokens": 1024,
                            "responseMimeType": "application/json",
                            "responseSchema": self.response_schema
                        },
                        "safetySettings": [
                            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                        ]
                    }
                }
                f.write(json.dumps(request) + "\n")
        # Upload file via Files API
        print(f"Uploading Gemini batch file ({len(sumerian_texts)} requests)...")
        from google.genai import types
        uploaded_file = self.client.files.upload(
            file=str(batch_file_path),
            config=types.UploadFileConfig(mime_type="application/x-ndjson")
        )
        
        print(f"Creating Gemini batch job...")
        batch_job = self.client.batches.create(
            model=self.model,
            src=uploaded_file.name,
            config={"display_name": f"sumerian-{uuid.uuid4().hex[:8]}"}
        )
        
        print(f"Polling Gemini batch {batch_job.name}...")
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Gemini batch timed out after {timeout}s")
            
            status = self.client.batches.get(name=batch_job.name)
            state = status.state.name
            print(f"  Gemini batch: {state}")
            
            if state == "JOB_STATE_SUCCEEDED":
                break
            elif state in ["JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"]:
                error_info = getattr(status, 'error', 'Unknown error')
                raise ValueError(f"Gemini batch failed: {state} - {error_info}")
            
            time.sleep(poll_interval)
        
        print("Downloading Gemini batch results...")
        result_file_name = status.dest.file_name
        file_content_bytes = self.client.files.download(file=result_file_name)
        file_content = file_content_bytes.decode("utf-8")
        
        results_by_key = {}
        for line in file_content.strip().split("\n"):
            if not line:
                continue
                
            obj = json.loads(line)
            key = obj.get("key", f"trans_{len(results_by_key)}")
            
            if "response" in obj:
                try:
                    resp_text = obj["response"]["candidates"][0]["content"]["parts"][0]["text"]
                    
                    try:
                        result_json = json.loads(resp_text)
                        translation = result_json.get("translation", "")
                        confidence = result_json.get("confidence", "medium")
                        notes = result_json.get("notes", "")
                    except json.JSONDecodeError:
                        translation = resp_text
                        confidence = "medium"
                        notes = "Raw text response (not structured JSON)"
                    
                    usage_meta = obj["response"].get("usageMetadata", {})
                    
                    results_by_key[key] = {
                        "custom_id": key,
                        "translation": translation,
                        "confidence": confidence,
                        "notes": notes,
                        "model": self.model,
                        "usage": {
                            "input_tokens": usage_meta.get("promptTokenCount", 0),
                            "output_tokens": usage_meta.get("candidatesTokenCount", 0)
                        }
                    }
                except (KeyError, IndexError) as e:
                    results_by_key[key] = {
                        "custom_id": key,
                        "translation": "",
                        "confidence": "error",
                        "notes": f"Batch result parse error: {str(e)}",
                        "model": self.model,
                        "usage": {"input_tokens": 0, "output_tokens": 0}
                    }
            else:
                error_msg = obj.get("status", {}).get("message", "Unknown error")
                results_by_key[key] = {
                    "custom_id": key,
                    "translation": "",
                    "confidence": "error",
                    "notes": f"Batch error: {error_msg}",
                    "model": self.model,
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                }
        
        results = []
        for i in range(len(sumerian_texts)):
            key = f"trans_{i}"
            if key in results_by_key:
                results.append(results_by_key[key])
            else:
                results.append({
                    "custom_id": key,
                    "translation": "",
                    "confidence": "error",
                    "notes": "Missing from batch results",
                    "model": self.model,
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                })
        
        return results