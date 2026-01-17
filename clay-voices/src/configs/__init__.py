"""Configuration components for language-agnostic prompt generation."""

from .languages import SUMERIAN_CONFIG, EGYPTIAN_CONFIG
from .roles import EXPERT_ROLE, SCRIBE_ROLE, FINKEL_ROLE, MINIMAL_ROLE
from .formats import STANDARD_FORMAT

__all__ = [
    "SUMERIAN_CONFIG",
    "EGYPTIAN_CONFIG",
    "EXPERT_ROLE",
    "SCRIBE_ROLE", 
    "FINKEL_ROLE",
    "MINIMAL_ROLE",
    "STANDARD_FORMAT"
]