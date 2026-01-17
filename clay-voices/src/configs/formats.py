"""Prompt format configurations."""

from dataclasses import dataclass


@dataclass
class FormatConfig:
    """Configuration for prompt formatting/structure."""
    
    name: str
    example_template: str
    example_separator: str
    test_template: str
    instruction_placement: str
    instruction_text: str


# Standard format (current approach)
STANDARD_FORMAT = FormatConfig(
    name="standard",
    example_template="Example {n}:\n{source_lang}: {source_text}\nEnglish: {target_text}\n",
    example_separator="\n",
    test_template="Now translate this {source_lang} text to English:\n\n{source_lang}: {test_text}\nEnglish:",
    instruction_placement="before_test",
    instruction_text="Translate the following text accurately."
)


# Inline format (more compact)
INLINE_FORMAT = FormatConfig(
    name="inline",
    example_template="{source_text} → {target_text}",
    example_separator=" | ",
    test_template="{test_text} →",
    instruction_placement="before_examples",
    instruction_text="Translate {source_lang} to English:"
)


# Chain-of-thought format
COT_FORMAT = FormatConfig(
    name="cot",
    example_template="{source_lang}: {source_text}\nThinking: [analyze structure]\nEnglish: {target_text}\n",
    example_separator="\n---\n",
    test_template="{source_lang}: {test_text}\nThinking:",
    instruction_placement="before_examples",
    instruction_text="Analyze each text's grammatical structure before translating."
)