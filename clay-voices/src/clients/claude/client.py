"""Anthropic Claude client with structured outputs and batch support."""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from anthropic import Anthropic

from ..unified.base import BaseTranslationClient
from ..unified.tools import TranslationTool


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