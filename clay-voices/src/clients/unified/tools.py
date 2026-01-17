"""Tool schema definitions for structured translation output across providers."""

from typing import Dict, Any


class TranslationTool:
    """Tool definitions for structured translation output across providers."""
    
    @staticmethod
    def get_anthropic_schema() -> Dict[str, Any]:
        """Return Anthropic tool schema."""
        return {
            "name": "translate_text",
            "description": "Translate Sumerian text to English with metadata",
            "input_schema": {
                "type": "object",
                "properties": {
                    "translation": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "notes": {"type": "string"}
                },
                "required": ["translation", "confidence"]
            }
        }
    
    @staticmethod
    def get_openai_schema() -> Dict[str, Any]:
        """Return OpenAI function schema (also used by Grok)."""
        return {
            "type": "function",
            "function": {
                "name": "translate_text",
                "description": "Translate Sumerian text to English with metadata",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "translation": {"type": "string"},
                        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                        "notes": {"type": "string"}
                    },
                    "required": ["translation", "confidence"]
                }
            }
        }
    
    @staticmethod
    def get_gemini_schema() -> Dict[str, Any]:
        """Return Gemini function declaration."""
        return {
            "name": "translate_text",
            "description": "Translate Sumerian text to English with metadata",
            "parameters": {
                "type": "object",
                "properties": {
                    "translation": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "notes": {"type": "string"}
                },
                "required": ["translation", "confidence"]
            }
        }
    
    @staticmethod
    def get_grok_schema() -> Dict[str, Any]:
        """Return Grok function schema (same as OpenAI - Grok is compatible)."""
        return TranslationTool.get_openai_schema()