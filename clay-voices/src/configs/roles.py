"""Role/persona configurations for translation prompts."""

from dataclasses import dataclass
from typing import List
from .languages import LanguageConfig, SUMERIAN_CONFIG, EGYPTIAN_CONFIG


@dataclass
class RoleConfig:
    """Configuration for an expert role/persona."""
    
    name: str
    persona: str
    expertise_description: str
    applicable_languages: List[str]
    translation_approach: str


def create_expert_role(language: LanguageConfig) -> RoleConfig:
    """Create a generic expert translator role for any language.
    
    Args:
        language: Language configuration
        
    Returns:
        Expert role configuration for that language
    """
    return RoleConfig(
        name="default",
        persona=f"You are an expert translator specializing in {language.display_name}.",
        expertise_description=f"{language.display_name} is a {language.family} language written in {language.script} script from the {language.period}.",
        applicable_languages=[language.name],
        translation_approach="Provide literal, scholarly translations that preserve the meaning and grammatical structure of the original text."
    )


def create_scribe_role(language: LanguageConfig) -> RoleConfig:
    """Create a native scribe persona for any language.
    
    Args:
        language: Language configuration
        
    Returns:
        Scribe role configuration
    """
    return RoleConfig(
        name="scribe",
        persona=f"You are an ancient {language.display_name} scribe from the {language.period}.",
        expertise_description=f"You have spent your life reading and writing {language.script} texts. You understand the language natively and know the conventions of {', '.join(language.text_types[:2])}.",
        applicable_languages=[language.name],
        translation_approach="Translate concisely and accurately, as one scribe to another. Focus on the core meaning as you would read it."
    )


# Pre-defined role configurations

EXPERT_ROLE = create_expert_role(SUMERIAN_CONFIG)  # Default uses Sumerian
SCRIBE_ROLE = create_scribe_role(SUMERIAN_CONFIG)

# Irving Finkel - cuneiform specialist (Sumerian, Akkadian, etc.)
FINKEL_ROLE = RoleConfig(
    name="finkel",
    persona="You are Dr. Irving Finkel, Assistant Keeper of Ancient Mesopotamian script, languages and cultures at the British Museum.",
    expertise_description="You are one of the world's foremost experts in cuneiform, with decades of experience reading Sumerian and Akkadian tablets. You understand the historical context, administrative terminology, and linguistic nuances of ancient Near Eastern texts.",
    applicable_languages=["sumerian", "akkadian", "hittite"],  # Cuneiform languages
    translation_approach="Translate with your characteristic precision and scholarly accuracy. Provide concise, literal translations that preserve the original administrative or literary meaning."
)

# Minimal role (no persona)
MINIMAL_ROLE = RoleConfig(
    name="minimal",
    persona="",
    expertise_description="",
    applicable_languages=["*"],  # Wildcard - works for all
    translation_approach=""
)