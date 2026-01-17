"""Unified API clients for LLM translation with structured outputs and batch support."""

import os
import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from anthropic import Anthropic
from openai import OpenAI
from google import genai


class TranslationTool:
    """Tool definitions for structured translation output across providers."""
    
    @staticmethod
    def get_anthropic_schema() -> Dict[str, Any]:
        """Return Anthropic tool schema."""
        return {
            "name": "translate_text",
            "description": "Translate Sumerian text to English with metadata",
            "input_schema": {
                "type": "object",
                "properties": {
                    "translation": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "notes": {"type": "string"}
                },
                "required": ["translation", "confidence"]
            }
        }
    
    @staticmethod
    def get_openai_schema() -> Dict[str, Any]:
        """Return OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": "translate_text",
                "description": "Translate Sumerian text to English with metadata",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "translation": {"type": "string"},
                        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                        "notes": {"type": "string"}
                    },
                    "required": ["translation", "confidence"]
                }
            }
        }
    
    @staticmethod
    def get_gemini_schema() -> Dict[str, Any]:
        """Return Gemini function declaration."""
        return {
            "name": "translate_text",
            "description": "Translate Sumerian text to English with metadata",
            "parameters": {
                "type": "object",
                "properties": {
                    "translation": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "notes": {"type": "string"}
                },
                "required": ["translation", "confidence"]
            }
        }


class BaseTranslationClient:
    """Base class for translation clients with common interfaces."""
    
    SYSTEM_PROMPT = """You are an expert translator specializing in ancient Sumerian language. 
Sumerian is a language isolate from ancient Mesopotamia, written in cuneiform script.

Translate Sumerian transliterations (romanized cuneiform) into clear, accurate English.
Pay attention to:
- Common Sumerian grammatical patterns
- Historical and cultural context
- Typical administrative and economic terminology from Ur III period texts

Provide literal, scholarly translations that preserve meaning and structure."""
    
    def _build_user_prompt(
        self,
        sumerian_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None
    ) -> str:
        """Build user prompt with optional few-shot examples."""
        parts = []
        
        if few_shot_examples:
            parts.append("Here are example translations:\n")
            for i, (sum_ex, eng_ex) in enumerate(few_shot_examples, 1):
                parts.append(f"Example {i}:")
                parts.append(f"Sumerian: {sum_ex}")
                parts.append(f"English: {eng_ex}\n")
        
        parts.append("Now translate this text:")
        parts.append(f"Sumerian: {sumerian_text}")
        
        return "\n".join(parts)


class ClaudeClient(BaseTranslationClient):
    """Anthropic Claude client with structured outputs and batch support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
        
    def translate(
        self,
        sumerian_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Translate single text with structured output via tool calling.
        
        Args:
            sumerian_text: Text to translate (source language)
            few_shot_examples: Optional few-shot examples
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
            monolingual_base: Optional monolingual sentences for context priming
            prompt_builder: Optional ModularPromptBuilder for language-specific prompts
        """
        if prompt_builder:
            sys_prompt, user_prompt = prompt_builder.build(
                sumerian_text,
                few_shot_examples=few_shot_examples,
                monolingual_base=monolingual_base
            )
        else:
            from prompts import PromptBuilder
            
            sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT
            _, user_prompt = PromptBuilder.build_prompt(
                sumerian_text,
                few_shot_examples=few_shot_examples,
                include_system=False,
                monolingual_base=monolingual_base
            )
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=sys_prompt,
            messages=[{"role": "user", "content": user_prompt + "\nUse the translate_text tool to respond."}],
            tools=[TranslationTool.get_anthropic_schema()],
            tool_choice={"type": "tool", "name": "translate_text"}
        )
        
        for block in response.content:
            if block.type == "tool_use" and block.name == "translate_text":
                return {
                    "translation": block.input["translation"],
                    "confidence": block.input.get("confidence", "medium"),
                    "notes": block.input.get("notes", ""),
                    "model": self.model,
                    "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
                }
        raise ValueError("No tool use found in Claude response")
        
    def translate_batch(
        self,
        sumerian_texts: List[str],
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None,
        poll_interval: float = 30.0,
        timeout: float = 3600.0
    ) -> List[Dict[str, Any]]:
        """Translate batch using Anthropic Batch API (50% savings).
        
        Args:
            sumerian_texts: List of texts to translate
            few_shot_examples: Optional few-shot examples
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
            monolingual_base: Optional monolingual sentences for context priming
            prompt_builder: Optional ModularPromptBuilder for language-specific prompts
            poll_interval: Seconds between status checks
            timeout: Maximum wait time
        """
        batch_requests = []
        
        for i, sumerian_text in enumerate(sumerian_texts):
            if prompt_builder:
                sys_prompt, user_prompt = prompt_builder.build(
                    sumerian_text,
                    few_shot_examples=few_shot_examples,
                    monolingual_base=monolingual_base
                )
            else:
                from prompts import PromptBuilder
                
                sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT
                _, user_prompt = PromptBuilder.build_prompt(
                    sumerian_text,
                    few_shot_examples=few_shot_examples,
                    include_system=False,
                    monolingual_base=monolingual_base
                )
            
            batch_requests.append({
                "custom_id": f"trans_{i}",
                "params": {
                    "model": self.model,
                    "max_tokens": 1024,
                    "system": sys_prompt,
                    "messages": [{"role": "user", "content": user_prompt + "\nUse translate_text tool."}],
                    "tools": [TranslationTool.get_anthropic_schema()],
                    "tool_choice": {"type": "tool", "name": "translate_text"}
                }
            })
        
        print(f"Submitting Anthropic batch ({len(batch_requests)} requests)...")
        batch = self.client.messages.batches.create(requests=batch_requests)
        
        # Robust polling with timeout
        print(f"Polling batch {batch.id}...")
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Claude batch timed out after {timeout}s")
            
            status = self.client.messages.batches.retrieve(batch.id)
            state = getattr(status.processing_status, 'state', str(status.processing_status))
            
            print(f"  Claude batch: {state}")
            
            if state in ["ended", "complete", "succeeded"]:
                break
            elif state in ["failed", "error", "cancelled"]:
                raise ValueError(f"Claude batch failed with state: {state}")
            
            time.sleep(poll_interval)
        
        # Retrieve results - ensure one result per request
        results = []
        results_by_id = {}
        
        try:
            for result in self.client.messages.batches.results(batch.id):
                if result.result.type == "succeeded":
                    for block in result.result.message.content:
                        if block.type == "tool_use" and block.name == "translate_text":
                            results_by_id[result.custom_id] = {
                                "custom_id": result.custom_id,
                                "translation": block.input["translation"],
                                "confidence": block.input.get("confidence", "medium"),
                                "notes": block.input.get("notes", ""),
                                "model": self.model,
                                "usage": {"input_tokens": result.result.message.usage.input_tokens,
                                        "output_tokens": result.result.message.usage.output_tokens}
                            }
                            break
                else:
                    # Error case - still add entry
                    error_msg = str(getattr(result.result, 'error', 'Unknown error'))
                    results_by_id[result.custom_id] = {
                        "custom_id": result.custom_id,
                        "translation": "",
                        "confidence": "error",
                        "notes": f"Batch error: {error_msg}",
                        "model": self.model,
                        "usage": {"input_tokens": 0, "output_tokens": 0}
                    }
        except Exception as e:
            print(f"Error retrieving batch results: {e}")
        
        # Ensure one result per input (fill missing with errors)
        for i in range(len(sumerian_texts)):
            custom_id = f"trans_{i}"
            if custom_id in results_by_id:
                results.append(results_by_id[custom_id])
            else:
                results.append({
                    "custom_id": custom_id,
                    "translation": "",
                    "confidence": "error",
                    "notes": "Missing from batch results",
                    "model": self.model,
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                })
        
        return results


class GPT5Client(BaseTranslationClient):
    """OpenAI GPT-5.2 client with function calling and batch support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5.2-instant"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        
    def translate(
        self,
        sumerian_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate single text with function calling.
        
        Args:
            sumerian_text: Text to translate
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
        """
        user_prompt = self._build_user_prompt(sumerian_text, few_shot_examples)
        sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            functions=[TranslationTool.get_openai_schema()["function"]],
            function_call={"name": "translate_text"},
            max_tokens=1024
        )
        
        func_call = response.choices[0].message.function_call
        if func_call and func_call.name == "translate_text":
            args = json.loads(func_call.arguments)
            return {
                "translation": args["translation"],
                "confidence": args.get("confidence", "medium"),
                "notes": args.get("notes", ""),
                "model": self.model,
                "usage": {"input_tokens": response.usage.prompt_tokens, "output_tokens": response.usage.completion_tokens}
            }
        raise ValueError("No function call found in GPT response")
    
    def translate_batch(
        self,
        sumerian_texts: List[str],
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        poll_interval: float = 60.0,
        timeout: float = 3600.0
    ) -> List[Dict[str, Any]]:
        """Translate batch using OpenAI Batch API.
        
        Args:
            sumerian_texts: List of texts
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
            poll_interval: Polling interval
            timeout: Max wait time
        """
        batch_file_path = Path(f"/tmp/openai_batch_{uuid.uuid4().hex[:8]}.jsonl")
        sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT

        with open(batch_file_path, 'w') as f:
            for i, sumerian_text in enumerate(sumerian_texts):
                user_prompt = self._build_user_prompt(sumerian_text, few_shot_examples)
                request = {
                    "custom_id": f"trans_{i}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "functions": [TranslationTool.get_openai_schema()["function"]],
                        "function_call": {"name": "translate_text"}
                    }
                }
                f.write(json.dumps(request) + "\n")
        
        print(f"Uploading OpenAI batch file ({len(sumerian_texts)} requests)...")
        with open(batch_file_path, "rb") as f:
            upload = self.client.files.create(file=f, purpose="batch")
        
        batch = self.client.batches.create(
            input_file_id=upload.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        
        # Poll with timeout
        print(f"Polling OpenAI batch {batch.id}...")
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"OpenAI batch timed out after {timeout}s")
            
            status = self.client.batches.retrieve(batch.id)
            print(f"  OpenAI batch: {status.status}")
            
            if status.status == "completed":
                break
            elif status.status in ("failed", "canceled", "expired"):
                raise ValueError(f"OpenAI batch failed: {status.status}")
            
            time.sleep(poll_interval)
        
        # Download and parse results
        result_content = self.client.files.content(status.output_file_id).read().decode("utf-8")
        
        results_by_id = {}
        for line in result_content.strip().split("\n"):
            obj = json.loads(line)
            custom_id = obj["custom_id"]
            
            if obj.get("error"):
                results_by_id[custom_id] = {
                    "custom_id": custom_id,
                    "translation": "",
                    "confidence": "error",
                    "notes": str(obj["error"]),
                    "model": self.model,
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                }
            else:
                func_call = obj["response"]["choices"][0]["message"]["function_call"]
                args = json.loads(func_call["arguments"])
                usage = obj["response"]["usage"]
                results_by_id[custom_id] = {
                    "custom_id": custom_id,
                    "translation": args["translation"],
                    "confidence": args.get("confidence", "medium"),
                    "notes": args.get("notes", ""),
                    "model": self.model,
                    "usage": {"input_tokens": usage["prompt_tokens"], "output_tokens": usage["completion_tokens"]}
                }
        
        # Ensure one result per input in order
        results = []
        for i in range(len(sumerian_texts)):
            custom_id = f"trans_{i}"
            if custom_id in results_by_id:
                results.append(results_by_id[custom_id])
            else:
                results.append({
                    "custom_id": custom_id,
                    "translation": "",
                    "confidence": "error",
                    "notes": "Missing from batch results",
                    "model": self.model,
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                })
        
        return results


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
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate single text using Gemini structured outputs.
        
        Args:
            sumerian_text: Text to translate
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
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
        poll_interval: float = 60.0,
        timeout: float = 7200.0
    ) -> List[Dict[str, Any]]:
        """Translate batch using Gemini Batch API (50% savings, 24h SLO).
        
        Args:
            sumerian_texts: List of texts
            few_shot_examples: Optional examples  
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
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