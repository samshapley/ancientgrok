"""OpenAI GPT client with function calling and batch support."""

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from ..unified.base import BaseTranslationClient
from ..unified.tools import TranslationTool


class GPT5Client(BaseTranslationClient):
    """OpenAI GPT-5.2 client with function calling and batch support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        
    def translate(
        self,
        sumerian_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        system_prompt: Optional[str] = None,
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Translate single text with function calling.
        
        Args:
            sumerian_text: Text to translate
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
            monolingual_base: Optional monolingual sentences (ignored for now)
            prompt_builder: Optional ModularPromptBuilder (not supported yet)
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
        monolingual_base: Optional[List[str]] = None,
        prompt_builder: Optional[Any] = None,
        poll_interval: float = 60.0,
        timeout: float = 3600.0
    ) -> List[Dict[str, Any]]:
        """Translate batch using OpenAI Batch API.
        
        Args:
            sumerian_texts: List of texts
            few_shot_examples: Optional examples
            system_prompt: Custom system prompt (defaults to SYSTEM_PROMPT)
            monolingual_base: Optional monolingual sentences (ignored for now)
            prompt_builder: Optional ModularPromptBuilder (not supported yet)
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