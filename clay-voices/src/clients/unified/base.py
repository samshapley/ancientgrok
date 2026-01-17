"""Base translation client with common interfaces."""

from typing import List, Optional, Tuple


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