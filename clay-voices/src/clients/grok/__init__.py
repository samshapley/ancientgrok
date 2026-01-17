"""xAI Grok clients for translation.

Provides two implementations:
- GrokChatClient: Chat Completions API (OpenAI-compatible, legacy)
- GrokAgenticClient: Responses API (modern, with hybrid tool calling)
"""

from .client import GrokChatClient, GrokAgenticClient

__all__ = ["GrokChatClient", "GrokAgenticClient"]