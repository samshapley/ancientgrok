"""xAI Grok clients - both Chat Completions (legacy) and Responses (modern) APIs."""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from ..unified.base import BaseTranslationClient
from ..unified.tools import TranslationTool


class GrokChatClient(BaseTranslationClient):
    """xAI Grok client using Chat Completions API (OpenAI-compatible, legacy).
    
    Uses OpenAI SDK with Grok base URL for simple function calling.
    Supports both reasoning and non-reasoning variants of Grok models.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "grok-4-1-fast-reasoning"):
        self.client = OpenAI(
            api_key=api_key or os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        self.model = model
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        
    def translate(
        self,
        sumerian_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Translate using Grok Chat Completions API with function calling.
        
        Args:
            sumerian_text: Text to translate
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt
            monolingual_base: Optional (ignored for this API)
            prompt_builder: Optional ModularPromptBuilder
        """
        if prompt_builder:
            sys_prompt, user_prompt = prompt_builder.build(
                sumerian_text,
                few_shot_examples=few_shot_examples,
                monolingual_base=monolingual_base
            )
        else:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from prompts import PromptBuilder
            
            sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT
            _, user_prompt = PromptBuilder.build_prompt(
                sumerian_text,
                few_shot_examples=few_shot_examples,
                include_system=False,
                monolingual_base=monolingual_base
            )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            tools=[{
                "type": "function",
                "function": TranslationTool.get_grok_schema()["function"]
            }],
            tool_choice={"type": "function", "function": {"name": "translate_text"}},
            max_tokens=1024
        )
        
        # Extract from function call
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.function.name == "translate_text":
                    args = json.loads(tool_call.function.arguments)
                    return {
                        "translation": args["translation"],
                        "confidence": args.get("confidence", "medium"),
                        "notes": args.get("notes", ""),
                        "model": self.model,
                        "usage": {
                            "input_tokens": response.usage.prompt_tokens,
                            "output_tokens": response.usage.completion_tokens
                        }
                    }
        
        raise ValueError("No translate_text function call in Grok response")
    
    def translate_batch(
        self,
        sumerian_texts: List[str],
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None,
        poll_interval: float = 30.0,
        timeout: float = 7200.0
    ) -> List[Dict[str, Any]]:
        """Translate batch using Grok Batch API (two-step process).
        
        Args:
            sumerian_texts: List of texts
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt
            monolingual_base: Optional monolingual sentences
            prompt_builder: Optional ModularPromptBuilder
            poll_interval: Polling interval (seconds)
            timeout: Max wait time (seconds)
        
        Returns:
            List of translation results
        """
        import httpx
        import uuid
        import time
        
        # Prepare system prompt
        if prompt_builder:
            sys_prompt, _ = prompt_builder.build(
                sumerian_texts[0] if sumerian_texts else "",
                few_shot_examples=few_shot_examples,
                monolingual_base=monolingual_base
            )
        else:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from prompts import PromptBuilder
            
            sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT
        
        # Step 1: Create batch container
        print(f"Creating Grok batch ({len(sumerian_texts)} requests)...")
        
        batch_name = f"sumerian-{uuid.uuid4().hex[:8]}"
        
        create_response = httpx.post(
            "https://api.x.ai/v1/batches",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            json={"name": batch_name},
            timeout=60.0
        )
        create_response.raise_for_status()
        batch_data = create_response.json()
        batch_id = batch_data.get("batch_id")
        
        print(f"Batch created: {batch_id}")
        
        # Step 2: Build and submit batch requests
        print("Submitting batch requests...")
        
        batch_requests = []
        for i, sumerian_text in enumerate(sumerian_texts):
            if prompt_builder:
                _, user_prompt = prompt_builder.build(
                    sumerian_text,
                    few_shot_examples=few_shot_examples,
                    monolingual_base=monolingual_base
                )
            else:
                _, user_prompt = PromptBuilder.build_prompt(
                    sumerian_text,
                    few_shot_examples=few_shot_examples,
                    include_system=False,
                    monolingual_base=monolingual_base
                )
            
            batch_requests.append({
                "batch_request_id": f"trans_{i}",
                "batch_request": {
                    "chat_get_completion": {
                        "messages": [
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "model": self.model,
                        "tools": [{
                            "type": "function",
                            "function": TranslationTool.get_grok_schema()["function"]
                        }],
                        "tool_choice": {"type": "function", "function": {"name": "translate_text"}},
                        "max_tokens": 1024
                    }
                }
            })
        
        # Submit requests (in chunks to respect 100 calls/30s limit AND 25MB payload limit)
        chunk_size = 10
        for i in range(0, len(batch_requests), chunk_size):
            chunk = batch_requests[i:i + chunk_size]
            
            add_response = httpx.post(
                f"https://api.x.ai/v1/batches/{batch_id}/requests",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={"batch_requests": chunk},
                timeout=60.0
            )
            add_response.raise_for_status()
            
            print(f"Submitted {len(chunk)} requests ({i+len(chunk)}/{len(batch_requests)})")
            
            # Rate limiting between chunks
            if i + chunk_size < len(batch_requests):
                time.sleep(1)  # Be conservative with rate limits
        
        # Step 3: Poll for completion
        print(f"Polling batch {batch_id}...")
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Grok batch timed out after {timeout}s")
            
            status_response = httpx.get(
                f"https://api.x.ai/v1/batches/{batch_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            
            # Extract processing status - Grok returns state as counters object
            state_obj = status_data.get("state", {})
            num_requests = state_obj.get("num_requests", 0)
            num_pending = state_obj.get("num_pending", 0)
            num_success = state_obj.get("num_success", 0)
            num_error = state_obj.get("num_error", 0)
            
            # Batch is complete when no requests are pending
            is_complete = (num_pending == 0 and num_requests > 0)
            has_errors = (num_error > 0)
            
            print(f"  Grok batch: {num_success}/{num_requests} success, {num_pending} pending, {num_error} errors")
            
            # Check for completion
            if is_complete and num_success > 0:
                break
            elif is_complete and num_error == num_requests:
                raise ValueError(f"Grok batch failed: all {num_error} requests errored")
            
            time.sleep(poll_interval)
        
        # Step 4: Retrieve results with pagination support
        print("Retrieving Grok batch results...")
        
        all_results = []
        pagination_token = None
        page_num = 1
        
        while True:
            # Build URL with pagination token if present
            results_url = f"https://api.x.ai/v1/batches/{batch_id}/results"
            if pagination_token:
                results_url += f"?pagination_token={pagination_token}"
            
            results_response = httpx.get(
                results_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=60.0
            )
            results_response.raise_for_status()
            results_data = results_response.json()
            
            # Collect results from this page
            page_results = results_data.get("results", [])
            all_results.extend(page_results)
            
            print(f"  Retrieved page {page_num}: {len(page_results)} results (total: {len(all_results)})")
            
            # Check for next page
            pagination_token = results_data.get("pagination_token")
            if not pagination_token:
                break  # No more pages
            
            page_num += 1
        
        print(f"Total results retrieved: {len(all_results)}")
        
        # Parse results into framework format
        results_by_id = {}
        
        # Process all results from all pages
        for result_item in all_results:
            custom_id = result_item.get("batch_request_id")
            
            # Navigate nested structure: batch_result → response → chat_get_completion
            batch_result = result_item.get("batch_result", {})
            response_wrapper = batch_result.get("response", {})
            response_data = response_wrapper.get("chat_get_completion", {})
            
            if not response_data:
                # Error case - no completion data
                results_by_id[custom_id] = {
                    "custom_id": custom_id,
                    "translation": "",
                    "confidence": "error",
                    "notes": "No completion data in batch result",
                    "model": self.model,
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                }
                continue
                
            if "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]
                
                # Extract from tool call
                if "message" in choice and "tool_calls" in choice["message"]:
                    for tool_call in choice["message"]["tool_calls"]:
                        if tool_call["function"]["name"] == "translate_text":
                            args = json.loads(tool_call["function"]["arguments"])
                            usage = response_data.get("usage", {})
                            
                            results_by_id[custom_id] = {
                                "custom_id": custom_id,
                                "translation": args["translation"],
                                "confidence": args.get("confidence", "medium"),
                                "notes": args.get("notes", ""),
                                "model": self.model,
                                "usage": {
                                    "input_tokens": usage.get("prompt_tokens", 0),
                                    "output_tokens": usage.get("completion_tokens", 0)
                                }
                            }
                            break
        
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


class GrokAgenticClient(BaseTranslationClient):
    """xAI Grok client using Responses API with hybrid tool calling (modern).
    
    Uses xai-sdk with client-side tools for structured outputs.
    Optionally supports server-side tools (web search, code execution) for research.
    
    Server-side tools cost $5 per 1000 calls in addition to token costs.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "grok-4-1-fast-reasoning",
        enable_web_search: bool = False,
        enable_x_search: bool = False,
        enable_code_execution: bool = False
    ):
        """Initialize Grok Agentic client with optional server-side tools.
        
        Args:
            api_key: xAI API key (defaults to XAI_API_KEY env var)
            model: Model name (grok-4-1-fast-reasoning or grok-4-1-fast-non-reasoning)
            enable_web_search: Enable autonomous web search for historical context
            enable_x_search: Enable X/Twitter search (rarely useful for ancient languages)
            enable_code_execution: Enable Python code execution for computational analysis
        """
        try:
            from xai_sdk import Client
            from xai_sdk.chat import user, system, tool
            from xai_sdk.tools import get_tool_call_type
        except ImportError:
            raise ImportError("xai-sdk required for Grok: pip install xai-sdk")
        
        self.Client = Client
        self.user = user
        self.system = system
        self.tool = tool
        self.get_tool_call_type = get_tool_call_type
        
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.model = model
        self.enable_web_search = enable_web_search
        self.enable_x_search = enable_x_search
        self.enable_code_execution = enable_code_execution
        
    def translate(
        self,
        sumerian_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Translate using Grok Responses API with client-side tool calling.
        
        Args:
            sumerian_text: Text to translate
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt
            monolingual_base: Optional monolingual sentences
            prompt_builder: Optional ModularPromptBuilder
        """
        if prompt_builder:
            sys_prompt, user_prompt = prompt_builder.build(
                sumerian_text,
                few_shot_examples=few_shot_examples,
                monolingual_base=monolingual_base
            )
        else:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from prompts import PromptBuilder
            
            sys_prompt = system_prompt if system_prompt is not None else self.SYSTEM_PROMPT
            _, user_prompt = PromptBuilder.build_prompt(
                sumerian_text,
                few_shot_examples=few_shot_examples,
                include_system=False,
                monolingual_base=monolingual_base
            )
        
        # Create stateless chat
        client = self.Client(api_key=self.api_key, timeout=3600)
        
        # Use xai-sdk's tool() helper to create proper protobuf Tool object for client-side translate_text
        translate_tool = self.tool(
            name="translate_text",
            description="Translate Sumerian text to English with metadata",
            parameters={
                "type": "object",
                "properties": {
                    "translation": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "notes": {"type": "string"}
                },
                "required": ["translation", "confidence"]
            }
        )
        
        # Build tools list: always include client-side translate_text
        tools = [translate_tool]
        
        # Optionally add server-side tools for agentic research
        # Grok will autonomously decide whether to use these before calling translate_text
        if self.enable_web_search:
            tools.append("web_search")
        if self.enable_x_search:
            tools.append("x_search")
        if self.enable_code_execution:
            tools.append("code_execution")
        
        chat = client.chat.create(model=self.model, store_messages=False, tools=tools)
        
        chat.append(self.system(sys_prompt))
        chat.append(self.user(user_prompt + "\nUse the translate_text function to provide your translation."))
        
        # Sample - Grok may autonomously use server-side tools before calling translate_text
        response = chat.sample()
        
        # Extract translation from client-side tool call (defensive access)
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if self.get_tool_call_type(tool_call) == "client_side_tool":
                    if tool_call.function.name == "translate_text":
                        args = json.loads(tool_call.function.arguments)
                        
                        # Extract server-side tool usage metadata if available
                        server_tool_usage = {}
                        if hasattr(response, 'tool_usage') and response.tool_usage:
                            # tool_usage is a dict-like mapping of tool names to invocation counts
                            server_tool_usage = dict(response.tool_usage) if response.tool_usage else {}
                        
                        result = {
                            "translation": args["translation"],
                            "confidence": args.get("confidence", "medium"),
                            "notes": args.get("notes", ""),
                            "model": self.model,
                            "usage": {
                                "input_tokens": getattr(response.usage, 'prompt_tokens', 0) if hasattr(response, 'usage') else 0,
                                "output_tokens": getattr(response.usage, 'completion_tokens', 0) if hasattr(response, 'usage') else 0
                            }
                        }
                        
                        # Add server tool usage if any tools were used
                        if server_tool_usage:
                            result["server_tools_used"] = server_tool_usage
                        
                        return result
        
        raise ValueError("No client-side translate_text tool call found in Grok response")
    
    def translate_batch(
        self,
        sumerian_texts: List[str],
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None,
        poll_interval: float = 60.0,
        timeout: float = 3600.0
    ) -> List[Dict[str, Any]]:
        """Translate batch - sequential implementation."""
        print(f"Grok Responses batch: Sequential mode ({len(sumerian_texts)} requests)")
        results = []
        
        for i, text in enumerate(sumerian_texts):
            print(f"  Grok Responses: {i+1}/{len(sumerian_texts)}")
            try:
                result = self.translate(
                    text,
                    few_shot_examples=few_shot_examples,
                    system_prompt=system_prompt,
                    monolingual_base=monolingual_base,
                    prompt_builder=prompt_builder
                )
                result["custom_id"] = f"trans_{i}"
                results.append(result)
            except Exception as e:
                results.append({
                    "custom_id": f"trans_{i}",
                    "translation": "",
                    "confidence": "error",
                    "notes": f"Grok error: {str(e)}",
                    "model": self.model,
                    "usage": {"input_tokens": 0, "output_tokens": 0}
                })
        
        return results