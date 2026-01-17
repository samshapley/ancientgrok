"""Language-specific configuration for ancient language translation."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class LanguageConfig:
    """Configuration for a specific ancient language."""
    
    name: str
    display_name: str
    family: str
    script: str
    period: str
    conventions: Dict[str, str]
    common_vocabulary: Dict[str, str]
    text_types: List[str]
    grammatical_notes: str
    translation_style: str
    special_instructions: str


# Sumerian language configuration
SUMERIAN_CONFIG = LanguageConfig(
    name="sumerian",
    display_name="Sumerian",
    family="language isolate",
    script="cuneiform",
    period="Ur III period (c. 2100-2000 BCE)",
    conventions={
        "NUMB": "numerical placeholder",
        "sila3": "unit of volume (approximately 1 liter)",
        "gin": "shekel (unit of weight)",
        "gu4": "ox, cattle",
        "udu": "sheep"
    },
    common_vocabulary={
        "udu": "sheep",
        "gu": "ox",
        "lugal": "king",
        "dingir": "god",
        "ur-": "man/servant of (name prefix)",
        "kicib": "seal",
        "mu": "year"
    },
    text_types=["administrative records", "economic documents", "year names"],
    grammatical_notes="Sumerian uses postpositions and typically follows SOV (Subject-Object-Verb) word order. Ergative-absolutive case marking is common.",
    translation_style="literal and scholarly, preserve structure and administrative meaning",
    special_instructions="Most Ur III texts are economic/administrative records with formulaic language. Numbers are represented as NUMB. Be precise with units of measurement."
)


# Egyptian language configuration (PROPER CONTEXT - not Sumerian!)
EGYPTIAN_CONFIG = LanguageConfig(
    name="egyptian",
    display_name="Ancient Egyptian",
    family="Afro-Asiatic",
    script="hieroglyphic",
    period="Middle Egyptian (c. 2000-1300 BCE)",
    conventions={
        ".f": "possessive suffix (his)",
        ".s": "possessive suffix (her)",
        ".k": "possessive suffix (your, masculine)",
        ".T": "possessive suffix (your, feminine)",
        "r": "preposition (to/toward/against)",
        "n": "preposition/genitive (of/to/for)",
        "m": "preposition (in/with/from)",
        "Hr": "preposition (upon/under)"
    },
    common_vocabulary={
        "nsw": "king",
        "nTr": "god/divine",
        "pr": "house/temple",
        "wA": "who/which",
        "jw": "sentence particle (marks main clause)",
        "m": "negative particle (not)",
        "sA": "son",
        "Hmt": "wife"
    },
    text_types=["funerary texts", "literary works", "historical inscriptions", "religious texts"],
    grammatical_notes="Egyptian typically uses VSO (Verb-Subject-Object) word order. Triconsonantal roots are fundamental. Hieroglyphic transliterations represent consonantal skeletons; vowels are not written and must be inferred.",
    translation_style="literal with attention to Egyptian grammatical structure and idiomatic expressions",
    special_instructions="Hieroglyphic transliterations use consonantal roots only - vowels are not represented. Pay attention to prepositions (r, n, m, Hr) as they carry significant meaning. Many texts have religious or funerary contexts."
)