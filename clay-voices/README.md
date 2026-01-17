# ClayVoices: LLM Translation Benchmark for Ancient Languages

![ClayVoices Hero](hero_image.png)

A comprehensive evaluation framework for frontier Large Language Models on ancient language tasks spanning multiple writing systems and modalities.

## Achievements

### State-of-the-Art Results

**Grok 2000-Shot (NEW SOTA):**
- **23.90 BLEU** (grok-4-1-fast-non-reasoning, 2000-shot, 100 examples)
- **Beats previous SOTA** of 22.04 BLEU by 1.86 points (+8.4%)
- First demonstration of 2000-shot in-context learning
- Leverages Grok's 2M context window (impossible with Claude's 200K limit)

See [GROK_SOTA.md](GROK_SOTA.md) for complete details.

**Sumerian → English (Previous Results):**
- **22.04 BLEU** (Claude Opus 4.5, 1000-shot) - Previous SOTA
- First improvement since COLING 2020

**Egyptian Hieroglyphics → English:**
- **35.69 BLEU** (full test set, 1000-shot) - Achieves 84.5% of recent 42.22 BLEU SOTA
- Demonstrates cross-language generalization

**Vision Hieroglyph Recognition:**
- **100% accuracy** at 10-shot (Egyptian hieroglyphs)
- Validates vision in-context learning for ancient scripts

### Novel Research Contributions

1. First systematic LLM evaluation on ancient language translation
2. Multi-language benchmark (Sumerian-isolate, Egyptian-Afro-Asiatic)
3. Multi-modal capabilities (text translation + vision recognition)
4. Comprehensive learning curves (0-2000 shots, 40+ experiments)
5. Monolingual priming discovery (+37% at 0-shot, hurts at high-shot)
6. Persona prompting analysis (scribe +14% at low-shot)

## Overview

ClayVoices systematically evaluates modern LLMs (Claude, GPT-4, Gemini) on ancient language understanding:
- **Text translation** (Sumerian, Egyptian)
- **Vision recognition** (Egyptian hieroglyphs)  
- **Multi-shot learning** (0-2000 examples)
- **Prompt engineering** (4 persona variants)
- **Cost tracking** and analysis

## Datasets

**Integrated Corpora:**
- **Sumerian-English**: 8,116 train, 1,014 test (CDLI/Machine-Translation)
- **Egyptian-English**: 10,350 train, 1,295 test (EgyptianTranslation)
- **Sumerian Monolingual**: 1.47M sentences
- **Egyptian Hieroglyphs (vision)**: 18 glyph images with Gardiner codes

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd clayvoices

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API keys
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export GEMINI_API_KEY="your-key-here"
```

## Usage

Run from project root so Python can find the `src` package:

```bash
# Sumerian translation benchmarks
python src/benchmark.py --dataset sumerian --model claude-sonnet-4-20250514 --shots 0 1 3 5
python src/benchmark.py --dataset sumerian --model claude-opus-4-5-20251101 --shots 1000 --mode batch

# Egyptian translation benchmarks  
python src/benchmark.py --dataset egyptian --model claude-opus-4-5-20251101 --shots 100 500 1000 --mode batch

# Vision hieroglyph recognition
python test_vision_glyphs.py --shots 0 5 10

# Cost analysis
python src/cost_tracker.py analyze results/

# Custom configurations
python src/benchmark.py --dataset egyptian \
                       --model claude-opus-4-5-20251101 \
                       --shots 1000 \
                       --test-size 200 \
                       --mode batch \
                       --prompt-variant scribe
```

## Supported Models

clay-voices supports multiple frontier LLM providers with a unified interface:

| Provider | Models | API Type | Status |
|----------|--------|----------|--------|
| **Anthropic** | claude-opus-4-5, claude-sonnet-4 | Messages API | ✅ Tested (SOTA: 22.04 BLEU) |
| **xAI** | grok-4-1-fast-reasoning, grok-4-1-fast-non-reasoning, grok-3 | Chat Completions + Responses API | ✅ Tested |
| **OpenAI** | gpt-5.2-instant | Chat Completions | ✅ Ready |
| **Google** | gemini-3-pro-preview | Gemini API | ✅ Ready |

**Grok Models (NEW):**
- `grok-4-1-fast-reasoning`: 2M context window (industry-leading), optimized for reasoning
- `grok-4-1-fast-non-reasoning`: 2M context window, faster responses
- Both support Chat Completions API (OpenAI-compatible) and Responses API (agentic)

**Architecture:**
```
src/clients/
├── unified/          # Base classes & tool schemas
├── claude/           # Claude-specific implementation
├── openai/           # GPT-specific implementation
├── gemini/           # Gemini-specific implementation
└── grok/             # Grok dual-API implementation
    ├── GrokChatClient       # Chat Completions (legacy)
    └── GrokAgenticClient    # Responses API (modern)
```

### CLI Arguments

- `--dataset` - Which ancient language: 'sumerian' (default) or 'egyptian'
- `--model` - Model identifier (see table above)
- `--shots` - Few-shot example counts (space-separated, e.g., 0 10 100 1000)
- `--test-size` - Number of test examples (default: all)
- `--mode` - 'individual' (streaming) or 'batch' (50% savings)
- `--prompt-variant` - 'default', 'scribe', 'finkel', or 'minimal'
- `--monolingual-base-size` - Prepend N monolingual sentences (Sumerian only)

### Individual vs. Batch Mode

- **Individual**: Real-time streaming, immediate feedback, easier debugging
- **Batch**: Async processing, 50% cost savings, better for large experiments

## Project Structure

```
clayvoices/
├── data/                    # Parallel corpora
│   ├── sumerian_train.txt   # Sumerian cuneiform transliterations
│   ├── english_train.txt    # English translations
│   ├── egyptian_train.txt   # Egyptian hieroglyphic transliterations
│   ├── english_egy_train.txt # English translations (Egyptian)
│   └── *_test/val.txt       # Test and validation splits
├── src/
│   ├── configs/            # Modular prompt configurations
│   │   ├── languages.py    # SUMERIAN_CONFIG, EGYPTIAN_CONFIG
│   │   ├── roles.py        # Expert, scribe, finkel personas
│   │   └── formats.py      # Prompt structure templates
│   ├── data_loader.py      # Multi-language corpus loader
│   ├── api_clients.py      # Claude, GPT, Gemini clients
│   ├── prompt_builder.py   # Modular prompt composition
│   ├── prompts.py          # Legacy prompt builder (Sumerian)
│   ├── evaluator.py        # BLEU, chrF++ metrics
│   ├── benchmark.py        # Main experiment orchestrator
│   ├── cost_tracker.py     # Cost tracking and estimation
│   ├── analysis.py         # Results analysis
│   ├── visualize.py        # Learning curve plots
│   └── vision_glyph_recognition.py  # Vision-based hieroglyph recognition
├── tests/
│   ├── test_data_loader.py # Data loading tests
│   └── test_evaluator.py   # Evaluation tests
├── maestro/                 # Research session documentation
│   ├── session_1.md        # Initial Sumerian SOTA achievement
│   ├── session_2.md        # Multi-language extension
│   └── README.md
├── paper/                   # LaTeX research paper
│   ├── main.tex            # Paper manuscript
│   ├── references.bib      # Bibliography
│   └── compile.sh          # Build script
├── results/                 # Experiment outputs (gitignored)
├── setup.py                 # Package installation
├── requirements.txt         # Dependencies
├── CONTRIBUTING.md         # Contribution guidelines
├── test_vision_glyphs.py   # Vision experiment runner
└── README.md
```

## Results Format

Each experiment generates: `results/{model}_{n}shot_{variant}.json`

```json
{
  "experiment": {
    "model": "claude-opus-4-5-20251101",
    "dataset": "egyptian",
    "n_shot": 1000,
    "test_size": 1295,
    "system_prompt_variant": "default"
  },
  "cost": {
    "cost_usd": 109.27,
    "input_tokens": 42795420,
    "output_tokens": 182303
  },
  "metrics": {
    "bleu": {"score": 35.69},
    "chrf": {"score": 54.64}
  },
  "predictions": [...]
}
```

Plus summary: `results/summary_{model}_{variant}.json`

## Testing

```bash
# Run test suite
pytest tests/ -v

# All 10 tests should pass
```

## License

MIT - Original data from CDLI (Sumerian) and EgyptianTranslation (fayrose) under open licenses

## Citation

If you use ClayVoices in your research, please cite:

```bibtex
@misc{clayvoices2025,
  title={ClayVoices: Frontier LLMs for Ancient Language Understanding},
  author={ClayVoices Research Team},
  year={2025},
  url={https://github.com/yourusername/clayvoices}
}
```

## Acknowledgments

We thank the CDLI, Oracc, Thesaurus Linguae Aegyptiae, and EgyptianTranslation projects for providing access to ancient language data. We acknowledge all Assyriologists, Egyptologists, and translators whose scholarly work enabled this research.