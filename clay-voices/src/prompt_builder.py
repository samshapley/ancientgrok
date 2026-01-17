"""Modular prompt builder using composable language, role, and format configurations."""

from typing import List, Tuple, Optional
from configs.languages import LanguageConfig
from configs.roles import RoleConfig
from configs.formats import FormatConfig


class ModularPromptBuilder:
    """Flexible prompt builder using swappable components."""
    
    def __init__(
        self,
        language_config: LanguageConfig,
        role_config: RoleConfig,
        format_config: FormatConfig
    ):
        """Initialize modular prompt builder.
        
        Args:
            language_config: Language-specific configuration
            role_config: Role/persona configuration
            format_config: Prompt structure configuration
        """
        self.language = language_config
        self.role = role_config
        self.format = format_config
        
        # Warn if role may not be suitable for language
        if (language_config.name not in role_config.applicable_languages 
            and "*" not in role_config.applicable_languages):
            print(f"Warning: Role '{role_config.name}' may not be optimal for {language_config.name}")
    
    def build_system_prompt(self) -> str:
        """Generate system prompt from language + role configs.
        
        Returns:
            Complete system prompt string
        """
        if self.role.name == "minimal":
            return ""  # No system prompt for minimal
        
        parts = []
        
        # Persona introduction
        if self.role.persona:
            parts.append(self.role.persona)
        
        # Language description (from expertise)
        if self.role.expertise_description:
            parts.append(f"\n{self.role.expertise_description}")
        
        # Transliteration conventions
        if self.language.conventions and self.role.name != "minimal":
            parts.append("\nTransliteration conventions:")
            for symbol, meaning in list(self.language.conventions.items())[:6]:  # Top 6
                parts.append(f"- {symbol}: {meaning}")
        
        # Common vocabulary
        if self.language.common_vocabulary and self.role.name != "minimal":
            parts.append("\nCommon vocabulary:")
            for word, meaning in list(self.language.common_vocabulary.items())[:5]:  # Top 5
                parts.append(f"- {word} ({meaning})")
        
        # Grammatical notes
        if self.language.grammatical_notes and self.role.name not in ["minimal", "scribe"]:
            parts.append(f"\n{self.language.grammatical_notes}")
        
        # Translation approach
        if self.role.translation_approach:
            parts.append(f"\n{self.role.translation_approach}")
        elif self.language.translation_style:
            parts.append(f"\nYour translations should be: {self.language.translation_style}")
        
        # Special instructions
        if self.language.special_instructions:
            parts.append(f"\n{self.language.special_instructions}")
        
        return "\n".join(parts)
    
    def build_user_prompt(
        self,
        test_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        monolingual_base: Optional[List[str]] = None
    ) -> str:
        """Generate user prompt with examples and test text.
        
        Args:
            test_text: Text to translate
            few_shot_examples: List of (source, target) translation pairs
            monolingual_base: Optional monolingual sentences for context
            
        Returns:
            Complete user prompt string
        """
        parts = []
        
        # Monolingual base (if provided)
        if monolingual_base and len(monolingual_base) > 0:
            parts.append(f"Here are {len(monolingual_base)} {self.language.display_name} text examples for context:\n")
            for i, text in enumerate(monolingual_base[:20], 1):
                parts.append(f"{i}. {text}")
            if len(monolingual_base) > 20:
                parts.append(f"... ({len(monolingual_base) - 20} more examples)\n")
        
        # Few-shot examples
        if few_shot_examples and len(few_shot_examples) > 0:
            if self.format.instruction_placement == "before_examples":
                parts.append(self.format.instruction_text.format(source_lang=self.language.display_name))
                parts.append("")
            
            parts.append("Here are example translations to guide you:\n")
            
            for i, (source, target) in enumerate(few_shot_examples, 1):
                example = self.format.example_template.format(
                    n=i,
                    source_lang=self.language.display_name,
                    source_text=source,
                    target_text=target
                )
                parts.append(example.rstrip())  # Remove trailing whitespace from template
        
        # Test sentence
        test_prompt = self.format.test_template.format(
            source_lang=self.language.display_name,
            test_text=test_text
        )
        parts.append(f"\n{test_prompt}")
        
        return "\n".join(parts)
    
    def build(
        self,
        test_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]] = None,
        monolingual_base: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """Build complete (system_prompt, user_prompt) tuple.
        
        Args:
            test_text: Text to translate
            few_shot_examples: Few-shot translation pairs
            monolingual_base: Monolingual context sentences
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system = self.build_system_prompt()
        user = self.build_user_prompt(test_text, few_shot_examples, monolingual_base)
        
        return system, user