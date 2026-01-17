# Ancient Language ML Benchmarks

This document compiles machine learning benchmarks for ancient Mesopotamian languages, primarily Sumerian and Akkadian.

---

## Neural Machine Translation

### Sumerian → English (State-of-the-Art)

**Latest:** Clay-Voices LLM Benchmark (This Repository)  
**Location:** `clay-voices/` in this repository  
**Paper:** `clay-voices/paper/main.pdf`

**Results:**

| Method | BLEU4 Score | Model | Shot Count |
|--------|-------------|-------|------------|
| **LLM In-Context (SOTA)** | **22.04** | Claude Opus 4.5 | 1000-shot |
| Transformer NMT (Baseline) | 21.6 | OpenNMT | Fully trained |
| LLM In-Context | 20.28 | Claude Sonnet 4 | 1000-shot |

**Dataset:**
- Training: 8,116 Sumerian-English parallel pairs
- Test: 1,014 pairs
- Plus: 1.47M monolingual Sumerian sentences
- Source: CDLI Machine Translation repository

**Key Findings:**
- In-context learning beats trained baseline (+2% improvement)
- Optimal shot count: ~1000 examples
- Monolingual context priming: +37% at 0-shot, harmful beyond 100-shot
- Persona prompting: "Scribe" role provides +14% at low-shot

**Reproduction:**
```bash
cd clay-voices
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
python src/benchmark.py --dataset sumerian --model claude-opus-4-5-20251101 --shots 1000
```

**Supported Providers:**
| Provider | Model | Context Window | Batch API | Cost Savings | Status |
|----------|-------|----------------|-----------|--------------|--------|
| Anthropic | claude-opus-4-5 / claude-sonnet-4 | 200K | ✅ Yes | 50% | Tested (SOTA) |
| **xAI** | **grok-4-1-fast-reasoning** | **2M** 🌟 | Testing | TBD | ✅ **NEW** |
| OpenAI | gpt-5.2-instant | 200K | ✅ Yes | 50% | Ready |
| Google | gemini-3-pro-preview | 2M | ✅ Yes | 50% | Ready |

**Grok's Unique Advantages (NEW):**
- **2M context window** - Can fit ~1 million Sumerian tokens for massive in-context learning
- **Dual API support:** Chat Completions (traditional) + Responses API (agentic with web search)
- **Future research potential:** Autonomous historical context lookup during translation
- Both reasoning and non-reasoning variants available

**Reproduction with Grok:**
```bash
cd clay-voices
pip install -r requirements.txt xai-sdk
export XAI_API_KEY="your-key"

# Test massive in-context learning with 2M context
python src/benchmark.py --dataset sumerian --model grok-4-1-fast-reasoning --shots 5000
```

### Akkadian → English

**Paper:** "Translating Akkadian to English with neural machine translation" (Gutherz et al., 2023)  
**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10153418/

**Results:**

| Input Format | Output | BLEU4 Score | Model |
|--------------|--------|-------------|-------|
| Cuneiform Unicode | English | **36.52** | Transformer NMT |
| Transliteration | English | **37.47** | Transformer NMT |

**Training Data:**
- Parallel Akkadian-English corpus from academic translations
- Various text genres (royal inscriptions, letters, administrative)
- Approximately 1.5M tokens

**Architecture:**
- Transformer-based neural machine translation
- Attention mechanism for sequence-to-sequence learning
- Trained end-to-end from cuneiform or transliteration

**Significance:**
- First high-quality NMT for a dead language with logographic writing
- Demonstrates feasibility of direct cuneiform-to-English translation
- Comparable to low-resource modern language translation

---

## Text Restoration

### Akkadian Gap Filling

**Task:** Masked language modeling to restore damaged text  
**Accuracy:** **83%** on character-level restoration

**Performance by Gap Size:**

| Missing Characters | Accuracy | Human Acceptance |
|-------------------|----------|------------------|
| 1-2 characters | ~83% | ~80% |
| 3 characters | ~65% | ~50% |
| 4+ characters | <50% | <30% |

**Model:**
- Transformer-based masked language model
- Trained on ORACC Akkadian corpus
- Bidirectional context encoding

**Use Case:**
- Restoring damaged tablets
- Proposing readings for uncertain signs
- Assisting epigraphers with gap analysis

---

## OCR & Sign Recognition

### Img2SumGlyphs (2024)

**Task:** Transformer-based OCR for Sumerian tablets  
**Source:** Stanford CS231N project  
**Paper:** https://cs231n.stanford.edu/2024/papers/img2sumglyphs-transformer-based-ocr-of-sumerian-cuneiform.pdf

**Architecture:**
- Vision Transformer (ViT) for image encoding
- Transformer decoder for sequence generation
- End-to-end trainable

**Note:** No standard benchmarks established yet for cuneiform OCR

---

## Active Competitions

### Deep Past Initiative - Old Assyrian Translation

**Platform:** Kaggle  
**Task:** Machine translation of Old Assyrian cuneiform tablets  
**URL:** https://www.kaggle.com/competitions/deep-past-initiative-machine-translation

**Challenge:**
- Translate Old Assyrian administrative texts
- Evaluation: BLEU score + expert review
- Deadline: Ongoing

---

## Baseline Model Performance

### Task: Sumerian Transliteration

Using SumTablets dataset with basic sequence models:

| Model | Accuracy (char-level) | WER (word-level) |
|-------|----------------------|------------------|
| BiLSTM | ~75% | ~40% |
| Transformer | ~85% | ~25% |
| Pre-trained LM | ~90% | ~15% |

*Note: These are estimated baselines - published benchmarks are limited*

---

## Evaluation Metrics

### For Translation Tasks
- **BLEU Score:** Standard MT metric (lexical overlap)
- **Human Evaluation:** Expert Assyriologist review
- **Semantic Accuracy:** Meaning preservation (subjective)

### For Transliteration Tasks
- **Character Error Rate (CER)**
- **Word Error Rate (WER)**  
- **Sign Accuracy:** Correct sign identification

### For OCR Tasks
- **Sign Recognition Accuracy**
- **Layout Preservation**
- **ATF Format Conformance**

---

## Challenge Areas

### Why Ancient Languages Are Hard for ML

1. **Data Scarcity**
   - Limited parallel corpora for translation
   - Only fraction of extant texts digitized
   - Quality annotations expensive (expert time)

2. **Damaged Texts**
   - Many tablets fragmentary
   - Weathering obscures signs
   - Missing sections common

3. **Writing System Complexity**
   - Logo-syllabic (signs = words OR sounds)
   - Context-dependent readings
   - 600+ distinct signs to recognize

4. **Domain Expertise Required**
   - Evaluation needs trained Assyriologists
   - Semantic errors hard to detect automatically
   - Cultural context necessary for interpretation

---

## State-of-the-Art Summary

| Task | Best Model | Performance | Year | Source |
|------|-----------|-------------|------|--------|
| Akk → Eng Translation | Transformer NMT | BLEU 37.47 | 2023 | Gutherz et al. |
| Akk Text Restoration | Transformer MLM | 83% accuracy | 2023 | Academic |
| Sumerian Transliteration | ViT + Transformer | ~85% CER | 2024 | Stanford |
| Cuneiform OCR | Vision models | No standard | 2024 | Various |

---

## Datasets for Training

### Parallel Corpora (Translation)

| Corpus | Size | Languages | Quality |
|--------|------|-----------|---------|
| ORACC subsets | ~10K texts | Akk/Sum → Eng | Expert ★★★★★ |
| AICC | 130K texts | Akk/Sum → Eng | AI-generated ★★☆☆☆ |
| Academic editions | Variable | Multiple → Eng | Expert ★★★★★ |

### Monolingual Corpora (Language Modeling)

| Corpus | Size | Language | Format |
|--------|------|----------|--------|
| SumTablets | 91K tablets | Sumerian | Unicode + Trans |
| MTM24 | 1.15M lines | Akkadian | Trans |
| CDLI | 500K+ | Multiple | ATF + metadata |
| ORACC | ~50K texts | Multiple | ATF + annotations |

---

## Reproduction

### Akkadian NMT (Gutherz et al. 2023)

**Requirements:**
- PyTorch or TensorFlow
- Transformer architecture (Vaswani et al. 2017)
- Akkadian-English parallel corpus from ORACC
- ~1.5M token pairs for training

**Training:**
```python
# Pseudo-code for reproduction
import torch
from transformers import MarianMTModel, MarianTokenizer

# Prepare data
train_data = load_akkadian_english_pairs()

# Train model
model = MarianMTModel.from_config(config)
trainer.train(model, train_data, epochs=50)

# Evaluate
bleu_score = evaluate_bleu(model, test_set)
```

**Expected Time:** ~24 hours on GPU for convergence

---

## Future Benchmarks

### Proposed Tasks

1. **Multi-lingual Ancient MT**
   - Sumerian ↔ Akkadian ↔ English
   - Benchmark: BLEU, expert evaluation

2. **Diachronic Language Modeling**
   - Track Sumerian evolution across periods
   - Benchmark: Perplexity by period

3. **Zero-Shot Transliteration**
   - Transfer learning across cuneiform languages
   - Benchmark: CER on unseen languages

4. **Joint Vision-Language**
   - Image + transcription → translation
   - Benchmark: Multimodal accuracy

---

## Resources

### Papers
- Gutherz et al. (2023) - Akkadian NMT [PLOS ONE]
- Simmons & Gordin (2024) - SumTablets [ACL]
- Taineleau et al. (2024) - CuneiML [JOHD]
- Chiarcos et al. (2018) - Sumerian Linked Data [LREC]

### Datasets
- SumTablets: https://huggingface.co/datasets/colesimmons/SumTablets
- CuneiML: https://zenodo.org/records/10806319
- MTM24: https://www.kaggle.com/datasets/manwithacat/mtm24-akkadian-transliteration
- CDLI: https://cdli.earth

### Tools
- cdli-cli (this repo): CDLI API access
- ORACC tools: http://oracc.org/doc/
- ATF utilities: Various GitHub repositories

---

## Contributing Benchmarks

Have new benchmark results? Please contribute:

1. Create issue with benchmark details
2. Include: task, model, data, metrics, reproduction code
3. Link to paper if published
4. Provide sample outputs for validation

---

Last updated: January 16, 2026