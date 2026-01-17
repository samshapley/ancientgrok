"""Prompt templates and construction for translation tasks."""

from typing import List, Tuple


class PromptBuilder:
    """Builds prompts for translation tasks with configurable few-shot examples."""
    
    # Default system prompt (expert translator)
    SYSTEM_PROMPT = """You are an expert translator specializing in ancient Sumerian language.
Sumerian is a language isolate from ancient Mesopotamia (c. 3100-2000 BCE), written in cuneiform script.

The transliterations you'll see are romanized representations of cuneiform signs following standard Assyriological conventions:
- Numbers are marked as NUMB
- Common words: udu (sheep), gu (ox), sila3 (unit of volume), gin (shekel)
- Names often contain divine elements: lugal (king), dingir (god), ur- (servant of)

Your translations should be:
- Literal and scholarly, preserving meaning and structure
- Aware of Ur III administrative context (most texts are economic records)
- Clear about uncertainties or ambiguities
"""

    # Sumerian scribe persona
    SCRIBE_PROMPT = """You are an ancient Sumerian scribe from the Ur III period (c. 2100-2000 BCE).
You have spent your life reading and writing cuneiform tablets in the administrative offices of Ur.
You understand the language natively and know the conventions of economic and administrative texts intimately.

The transliterations you see are romanized versions of the cuneiform signs you work with daily:
- NUMB represents numerical values
- Common terms: udu (sheep), gu (ox), sila3 (measure), gin (shekel), lugal (king)
- Administrative formulas like mu (year names), kicib (seal), giri (via/responsibility)

Translate these texts as you would read them - concisely and accurately, as one scribe to another.
Focus on the administrative meaning, not lengthy explanation."""

    # Irving Finkel persona (renowned cuneiformist)
    FINKEL_PROMPT = """You are Dr. Irving Finkel, Assistant Keeper of Ancient Mesopotamian script, languages and cultures at the British Museum.
You are one of the world's foremost experts in cuneiform, with decades of experience reading Sumerian and Akkadian tablets.
You understand the historical context, administrative terminology, and linguistic nuances of Ur III period texts.

The transliterations before you are romanized cuneiform following standard Assyriological conventions:
- NUMB marks numerical placeholders
- Common vocabulary: udu (sheep), gu (ox), sila3 (volume unit), gin (weight unit)
- Personal names often include divine elements: lugal (king), ur- (man/servant of)

Translate these administrative texts with your characteristic precision and scholarly accuracy.
Provide concise, literal translations that preserve the original administrative meaning."""

    # Minimal prompt (no persona, just task)
    MINIMAL_PROMPT = """Translate Sumerian transliterations to English."""

    @staticmethod
    def build_prompt(
        sumerian_text: str,
        few_shot_examples: List[Tuple[str, str]] = None,
        include_system: bool = True,
        system_prompt_variant: str = "default",
        monolingual_base: List[str] = None
    ) -> Tuple[str, str]:
        """Build system and user prompts.
        
        Args:
            sumerian_text: Sumerian text to translate
            few_shot_examples: List of (sumerian, english) example pairs
            include_system: Whether to include system prompt
            system_prompt_variant: Which system prompt to use ('default', 'scribe', 'finkel', 'minimal')
            monolingual_base: Optional list of monolingual Sumerian sentences to prepend as context
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Select system prompt variant
        if not include_system or system_prompt_variant == "minimal":
            system = PromptBuilder.MINIMAL_PROMPT
        elif system_prompt_variant == "scribe":
            system = PromptBuilder.SCRIBE_PROMPT
        elif system_prompt_variant == "finkel":
            system = PromptBuilder.FINKEL_PROMPT
        else:  # default
            system = PromptBuilder.SYSTEM_PROMPT
        
        user_parts = []
        
        # Prepend monolingual base if provided
        if monolingual_base and len(monolingual_base) > 0:
            user_parts.append(f"Here are {len(monolingual_base)} examples of Sumerian text for context:\n")
            for i, sumerian_ex in enumerate(monolingual_base[:20], 1):
                user_parts.append(f"{i}. {sumerian_ex}")
            if len(monolingual_base) > 20:
                user_parts.append(f"... ({len(monolingual_base) - 20} more examples)")
            user_parts.append("\n")
        
        if few_shot_examples:
            user_parts.append("Here are example translations to guide you:\n")
            for i, (sum_ex, eng_ex) in enumerate(few_shot_examples, 1):
                user_parts.append(f"Example {i}:")
                user_parts.append(f"Sumerian: {sum_ex}")
                user_parts.append(f"English: {eng_ex}\n")
        
        user_parts.append("Now translate this Sumerian text to English:")
        user_parts.append(f"\nSumerian: {sumerian_text}")
        user_parts.append("English:")
        
        return system, "\n".join(user_parts)
    
    @staticmethod
    def build_batch_prompt(
        sumerian_texts: List[str],
        few_shot_examples: List[Tuple[str, str]] = None
    ) -> str:
        """Build prompt for batched translation.
        
        Args:
            sumerian_texts: List of Sumerian texts
            few_shot_examples: Example pairs
            
        Returns:
            Batch prompt string
        """
        parts = []
        
        if few_shot_examples:
            parts.append("Here are example translations:\n")
            for sum_ex, eng_ex in few_shot_examples:
                parts.append(f"Sumerian: {sum_ex}")
                parts.append(f"English: {eng_ex}\n")
        
        parts.append("Translate each of the following Sumerian texts to English:")
        for i, text in enumerate(sumerian_texts, 1):
            parts.append(f"\n{i}. Sumerian: {text}")
            parts.append(f"   English:")
        
        return "\n".join(parts)