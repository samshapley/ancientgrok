# clayvoices Architecture

This document describes the architecture of the clayvoices repository, focusing on the multi-provider LLM benchmarking framework and how components interact.

---

## Repository Overview

clayvoices is organized into three main components:

```
clayvoices/
├── clay-voices/      # LLM benchmarking framework
├── cdli-cli/         # CDLI API access tool
└── data/, scripts/, docs/  # Shared resources
```

Each component is independent but designed to work together.

---

## clay-voices: Multi-Provider Benchmarking Framework

### Core Architecture Principles

1. **Provider Abstraction** - All LLM providers implement a common interface
2. **Modular Design** - Each provider in its own module
3. **Unified Output** - All providers return compatible data structures
4. **Flexible Prompting** - Configurable language/role/format combinations

### Directory Structure

```
clay-voices/
├── src/
│   ├── clients/              # Multi-provider architecture
│   │   ├── unified/         # Shared abstractions
│   │   │   ├── base.py      # BaseTranslationClient
│   │   │   └── tools.py     # TranslationTool schemas
│   │   ├── claude/          # Anthropic Claude
│   │   │   └── client.py    # ClaudeClient
│   │   ├── openai/          # OpenAI GPT
│   │   │   └── client.py    # GPT5Client
│   │   ├── gemini/          # Google Gemini
│   │   │   └── client.py    # GeminiClient
│   │   └── grok/            # xAI Grok (dual API)
│   │       └── client.py    # GrokChatClient + GrokAgenticClient
│   ├── configs/             # Modular prompt system
│   │   ├── languages.py     # Language-specific configs
│   │   ├── roles.py         # Persona/role configs
│   │   └── formats.py       # Prompt format templates
│   ├── benchmark.py         # Main orchestrator
│   ├── data_loader.py       # Parallel corpus loading
│   ├── evaluator.py         # BLEU, chrF++ metrics
│   ├── cost_tracker.py      # Cost estimation/tracking
│   └── visualize.py         # Result visualization
├── data/                    # Parallel corpora
│   ├── sumerian_train.txt   # Training data
│   ├── sumerian_test.txt    # Test data
│   ├── english_train.txt    # Training translations
│   └── english_test.txt     # Test translations
├── results/                 # Experimental outputs
├── paper/                   # Research paper (LaTeX)
└── tests/                   # Unit tests
```

---

## Multi-Provider Client Architecture

### Base Class: BaseTranslationClient

All provider clients extend `BaseTranslationClient` which defines:

**Required Methods:**
```python
class BaseTranslationClient:
    def translate(
        sumerian_text: str,
        few_shot_examples: Optional[List[Tuple[str, str]]],
        system_prompt: Optional[str],
        monolingual_base: Optional[List[str]],
        prompt_builder: Optional[Any]
    ) -> Dict[str, Any]:
        """Translate single text."""
        ...
    
    def translate_batch(
        sumerian_texts: List[str],
        # Same parameters as translate()
    ) -> List[Dict[str, Any]]:
        """Translate batch of texts."""
        ...
```

**Unified Output Format:**
```python
{
    "translation": str,       # English translation
    "confidence": str,        # "high" | "medium" | "low" | "error"
    "notes": str,             # Optional translator notes
    "model": str,             # Model identifier
    "usage": {
        "input_tokens": int,
        "output_tokens": int
    }
}
```

### Provider Implementations

| Provider | API Type | Key Features |
|----------|----------|--------------|
| **Claude** | Messages API | Tool calling, batch API (50% savings) |
| **GPT** | Chat Completions | Function calling, batch API (50% savings) |
| **Gemini** | Gemini API | Structured outputs, batch API (50% savings) |
| **Grok (Chat)** | Chat Completions | OpenAI-compatible, 2M context |
| **Grok (Agentic)** | Responses API | Hybrid tools, server-side execution |

### Tool Schema Adapters

The `TranslationTool` class provides format adapters for each provider:

```python
class TranslationTool:
    @staticmethod
    def get_anthropic_schema() -> dict:
        """Anthropic Messages API tools format."""
        ...
    
    @staticmethod
    def get_openai_schema() -> dict:
        """OpenAI function calling format (also used by Grok)."""
        ...
    
    @staticmethod
    def get_gemini_schema() -> dict:
        """Gemini function declarations format."""
        ...
    
    @staticmethod
    def get_grok_schema() -> dict:
        """Grok format (reuses OpenAI)."""
        return get_openai_schema()
```

These adapters ensure each provider gets tool definitions in its expected format while maintaining a unified interface.

---

## Benchmark Pipeline

### Execution Flow

```
1. Data Loading (data_loader.py)
   ├─ Load Sumerian-English parallel corpus
   ├─ Sample few-shot examples
   └─ Get test subset

2. Client Initialization (benchmark.py)
   ├─ Recognize model name → select provider
   └─ Initialize appropriate client

3. Translation (provider-specific client)
   ├─ Build prompt (with few-shot examples)
   ├─ Call provider API (individual or batch)
   └─ Extract structured output

4. Evaluation (evaluator.py)
   ├─ Compute BLEU score
   ├─ Compute chrF++ score
   └─ Analyze confidence distribution

5. Cost Tracking (cost_tracker.py)
   ├─ Count tokens
   ├─ Calculate cost per provider
   └─ Track batch savings

6. Results Storage
   ├─ Save predictions + metrics
   ├─ Save summary statistics
   └─ Generate visualizations
```

### Adding a New Provider

To add a new LLM provider (e.g., Anthropic Claude Haiku):

1. **Create provider module:**
   ```
   src/clients/provider_name/
   ├── __init__.py
   └── client.py
   ```

2. **Implement client class:**
   ```python
   class NewProviderClient(BaseTranslationClient):
       def translate(self, sumerian_text, ...):
           # Provider-specific API call
           # Return unified format
       
       def translate_batch(self, sumerian_texts, ...):
           # Provider-specific batch API
           # Return list of unified formats
   ```

3. **Add tool schema (if needed):**
   ```python
   # In unified/tools.py
   @staticmethod
   def get_newprovider_schema() -> dict:
       # Provider-specific tool format
   ```

4. **Register in benchmark.py:**
   ```python
   elif "newprovider" in model_name.lower():
       client = NewProviderClient(model=model_name)
   ```

5. **Test:**
   ```bash
   python src/benchmark.py --model newprovider-model-name --shots 10
   ```

---

## Modular Prompt System

Located in `src/configs/`, the prompt system separates concerns:

### Language Configuration (languages.py)

Defines language-specific knowledge:
- Conventions (e.g., "sila3" = unit of volume)
- Common vocabulary (e.g., "lugal" = king)
- Grammatical notes (e.g., SOV word order)
- Translation style guidelines

### Role Configuration (roles.py)

Defines expert personas:
- **Expert**: Generic translator specialist
- **Scribe**: Ancient scribe persona
- **Finkel**: Specific curator persona
- **Minimal**: No persona

### Format Configuration (formats.py)

Defines prompt structure templates (future expansion).

### Usage

```python
from prompt_builder import ModularPromptBuilder
from configs.languages import SUMERIAN_CONFIG
from configs.roles import SCRIBE_ROLE

builder = ModularPromptBuilder(SUMERIAN_CONFIG, SCRIBE_ROLE)
system_prompt, user_prompt = builder.build(sumerian_text, few_shot_examples)
```

---

## cdli-cli: CDLI API Access Tool

Independent production tool for accessing CDLI's 500,000+ artifacts.

**Architecture:**
- `client.py` - Comprehensive API client
- `main.py` - Typer-based CLI
- `models.py` - Data models and enums
- `schemas.py` - Pydantic validation
- `display.py` - Rich terminal formatting

**Key Features:**
- Content negotiation for multiple formats
- Image downloads via predictable URLs
- Error handling for upstream API issues
- Comprehensive test coverage (22 tests)

See [cdli-cli/docs/](cdli-cli/docs/) for detailed documentation.

---

## Data Management

### What's in Git (Small, Essential Data)

- ✅ Unicode cuneiform data (3MB)
- ✅ Clay-voices parallel corpus (8MB)
- ✅ Monolingual Sumerian text (15MB)
- ✅ Code, configurations, tests

**Total in repository: ~30MB**

### What's External (Large Datasets)

- ❌ SumTablets (500MB) - Download via scripts
- ❌ CuneiML (50GB) - Download via scripts
- ❌ MTM24 (200MB) - Download via scripts
- ❌ CDLI artifacts (on-demand) - Export via cdli-cli

All external datasets are gitignored and accessed via download scripts or API tools.

---

## Extension Points

### For Researchers

**Adding new experiments:**
- Modify `configs/` for new languages or personas
- Create new prompt templates in `prompt_builder.py`
- Add evaluation metrics in `evaluator.py`

**Adding new data sources:**
- Implement data loader in `data_loader.py`
- Add download script in `scripts/`
- Update documentation in `docs/DATASETS.md`

### For Developers

**Adding provider capabilities:**
- Implement batch API support in provider client
- Add vision capabilities (image input)
- Support structured outputs beyond tool calling

**Performance optimization:**
- Implement async/parallel API calls
- Add caching layers
- Optimize token usage

---

## Design Decisions

### Why Separate Provider Modules?

**Pros:**
- ✅ Clean separation of concerns
- ✅ Easy to add/remove providers
- ✅ Provider-specific features isolated
- ✅ Better for collaborative development

### Why Unified Output Format?

**Pros:**
- ✅ Provider-agnostic evaluation
- ✅ Easy to compare models
- ✅ Consistent downstream processing

### Why Modular Prompts?

**Pros:**
- ✅ Language-agnostic framework
- ✅ Reusable across experiments
- ✅ Easy to test prompt variants

---

## Testing Strategy

### Unit Tests (tests/)
- Data loading correctness
- Evaluation metric validation
- Output format verification

### Integration Tests
- End-to-end provider testing
- Benchmark pipeline validation
- Multi-provider compatibility

### Live Validation
- Small-scale benchmarks (10-shot, 50 examples)
- Multi-provider comparison runs
- Cost tracking verification

---

## Future Architecture Considerations

### Planned Enhancements

**Provider Registry Pattern:**
```python
PROVIDERS = {
    "anthropic": ClaudeClient,
    "openai": GPT5Client,
    "google": GeminiClient,
    "xai": GrokChatClient,
}

client = PROVIDERS[provider_name](model=model_name)
```

**Model Capability Metadata:**
```python
MODEL_CAPS = {
    "grok-4-1-fast": {
        "context": 2_000_000,
        "batch_api": True,
        "vision": False,
        "cost_per_1m": {"input": 0.20, "output": 0.50}
    }
}
```

**Configuration-Driven Execution:**
```yaml
experiment:
  model: grok-4-1-fast-reasoning
  dataset: sumerian
  shots: [10, 100, 1000]
  test_size: 100
  mode: batch
```

---

## Versioning and Releases

- **v0.1.0** - Initial clay-voices integration, CDLI CLI tool
- **v0.2.0** - Multi-provider architecture, Grok support
- **v1.0.0** - Planned: Complete benchmark suite, all providers tested

---

Last updated: January 17, 2026