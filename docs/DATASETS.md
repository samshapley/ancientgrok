# Ancient Language Datasets - Complete Catalog

This document provides a comprehensive catalog of all available datasets for Sumerian, Akkadian, and related ancient Mesopotamian languages.

---

## Dataset Overview

| Dataset | Language(s) | Size | Type | Access | License |
|---------|------------|------|------|--------|---------|
| **SumTablets** | Sumerian | 91,606 tablets | Glyphs ↔ Trans | Hugging Face | CC BY 4.0 |
| **CuneiML** | Sum/Akk | 38,947 photos | Images ↔ Trans | Zenodo | Open |
| **MTM24** | Akkadian | 1.15M lines | Cuneiform ↔ Trans | Kaggle | See page |
| **CDLI** | Multiple | 500,000+ | Metadata + Images | API | CC BY-SA 4.0 |
| **ORACC** | Multiple | Variable | Trans + Trans | Web/API | Various |
| **Unicode** | All cuneiform | 1,205 signs | Character data | Public | Public domain |

---

## Detailed Dataset Information

### 1. SumTablets

**Full Name:** SumTablets: A Transliteration Dataset of Sumerian Tablets  
**Source:** https://huggingface.co/datasets/colesimmons/SumTablets  
**Paper:** https://aclanthology.org/2024.ml4al-1.20/

**Statistics:**
- 91,606 Sumerian cuneiform tablets
- 6,970,407 total glyphs
- Unicode cuneiform representations
- Scholarly transliterations from ORACC

**Structure:**
```python
{
  "tablet_id": "P000001",
  "glyphs": "𒀀𒀁𒀂𒀃",  # Unicode cuneiform
  "transliteration": "a a-a bad gan2",  # Romanized
  "period": "Ur III",
  "provenance": "Girsu"
}
```

**Download:**
```bash
cd scripts
python download_sumtablets.py --output ../data/sumtablets
```

**Use Cases:**
- Transliteration model training
- Sign sequence analysis
- Sumerian NLP
- Statistical linguistics

**Citation:**
```bibtex
@inproceedings{simmons2024sumtablets,
  title={SumTablets: A Transliteration Dataset of Sumerian Tablets},
  author={Simmons, Cole and Gordin, Shai},
  booktitle={Proceedings of the 1st Workshop on Machine Learning for Ancient Languages},
  year={2024},
  publisher={ACL}
}
```

---

### 2. CuneiML

**Full Name:** CuneiML: A Cuneiform Dataset for Machine Learning  
**Source:** https://zenodo.org/records/10806319  
**Paper:** https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.151

**Statistics:**
- 38,947 high-resolution 2D photographs
- Sumerian and Akkadian texts
- Accompanied by transcriptions
- Various periods and text types

**Structure:**
- Image files (JPEG format)
- Transcription files (ATF format)
- Metadata CSV/JSON

**Download:**
```bash
cd scripts
# Metadata only (recommended first)
python download_cuneiml.py

# Full dataset with images (~50GB)
python download_cuneiml.py --images --output ../data/cuneiml
```

**Use Cases:**
- OCR model training
- Sign detection and recognition
- Image-to-text transformation
- Computer vision on ancient texts

**Citation:**
```bibtex
@article{taineleau2024cuneiml,
  title={CuneiML: A Cuneiform Dataset for Machine Learning},
  author={Taineleau et al.},
  journal={Journal of Open Humanities Data},
  year={2024},
  doi={10.5334/johd.151}
}
```

---

### 3. MTM24 Akkadian

**Full Name:** MTM24 Akkadian Cuneiform Transliteration Dataset  
**Source:** https://www.kaggle.com/datasets/manwithacat/mtm24-akkadian-transliteration  
**Method:** Maximum Entropy Markov Model transliteration

**Statistics:**
- 1,154,023 lines of Akkadian text
- Cuneiform to scholarly transliteration
- Various text genres and periods
- Line-by-line structure

**Format:**
CSV with columns for cuneiform signs and transliterations

**Download:**
```bash
cd scripts
python download_mtm24.py --output ../data/mtm24
```

**Prerequisites:**
- Kaggle API credentials configured
- `~/.kaggle/kaggle.json` with API key

**Use Cases:**
- Akkadian language modeling
- Transliteration normalization
- Large-scale corpus analysis
- Comparative Semitic linguistics

**Citation:**
```
MTM24 Akkadian Cuneiform Transliteration Dataset
Available at: https://www.kaggle.com/datasets/manwithacat/mtm24-akkadian-transliteration
Accessed: 2026
```

---

### 4. CDLI (On-Demand)

**Full Name:** Cuneiform Digital Library Initiative  
**Source:** https://cdli.earth  
**Access:** Via cdli-cli tool in this repository

**Statistics:**
- 500,000+ cuneiform artifacts
- Multiple languages (Sumerian, Akkadian, Elamite, Hittite, etc.)
- 3400 BCE - 75 CE coverage
- Images, transcriptions, metadata

**Access Methods:**

```bash
cd cdli-cli

# Search and export
cdli find "Ur III administrative" --per-page 1000 -o ../data/cdli/ur3.json

# Download images
cdli image photo P000001

# List metadata
cdli list periods -o ../data/cdli/periods.json
cdli list languages -o ../data/cdli/languages.json
```

**Available Data:**
- Search results (full artifact metadata)
- Images (photos + lineart tracings)
- Metadata (32 periods, 100+ collections, 44 languages, 87 genres)
- Bibliographies

**Use Cases:**
- On-demand corpus creation
- Specific period/genre research
- Image acquisition for OCR
- Metadata analysis

**Citation:**
```bibtex
@misc{cdli2026,
  author = {{CDLI Contributors}},
  title = {Cuneiform Digital Library Initiative},
  year = {2026},
  url = {https://cdli.earth}
}
```

---

### 5. Unicode Cuneiform

**Full Name:** Unicode Cuneiform Character Database  
**Source:** https://unicode.org  
**Location:** `data/unicode/`

**Statistics:**
- 1,205 cuneiform characters
- Covers Sumero-Akkadian signs
- Numeric signs (111)
- Early Dynastic signs (27)
- Cypro-Minoan (99)

**Contents:**
- `cuneiform_characters.txt` - Cuneiform-specific extraction (1,205 signs)
- `UnicodeData.txt` - Full Unicode database
- `Blocks.txt` - Unicode block definitions
- `NamesList.txt` - Extended character annotations

**Use Cases:**
- Character encoding reference
- Sign name lookup
- Unicode normalization
- Font development

---

## ML Benchmarks

### Neural Machine Translation

**Task:** Akkadian → English  
**Best Results:**
- Cuneiform → English: BLEU4 = 36.52
- Transliteration → English: BLEU4 = 37.47
- Architecture: Transformer NMT
- Source: Gutherz et al. (2023)

### Text Restoration

**Task:** Fill gaps in damaged Akkadian texts  
**Best Results:**
- 83% accuracy on masked language modeling
- ~50% human acceptance for 3+ character gaps
- Architecture: Transformer

See [docs/BENCHMARKS.md](docs/BENCHMARKS.md) for comprehensive benchmarks.

---

## Getting Started

### 1. Set Up CDLI Access

```bash
cd cdli-cli
pip install -e .
cdli --help
```

### 2. Download a Dataset

```bash
cd scripts
python download_sumtablets.py  # Starts download (~500MB)
```

### 3. Explore the Data

```python
from datasets import load_from_disk

# Load SumTablets
dataset = load_from_disk("data/sumtablets")
print(f"Loaded {len(dataset['train'])} Sumerian tablets")

# Inspect first tablet
first = dataset['train'][0]
print(first['glyphs'])           # Unicode cuneiform
print(first['transliteration'])  # Romanized text
```

---

## Repository Structure

```
clayvoices/
├── cdli-cli/              # CDLI API client tool
│   ├── src/cdli_cli/     # Python package
│   ├── tests/            # 22 unit tests
│   └── docs/             # Tool documentation
├── data/                  # Datasets directory
│   ├── unicode/          # Unicode cuneiform data ✅
│   ├── sumtablets/       # SumTablets ⏳
│   ├── cuneiml/          # CuneiML ⏳
│   └── mtm24/            # MTM24 Akkadian ⏳
├── scripts/               # Download automation
│   ├── download_sumtablets.py
│   ├── download_cuneiml.py
│   └── download_mtm24.py
├── docs/                  # Project documentation
│   ├── DATASETS.md       # Dataset catalog
│   ├── BENCHMARKS.md     # ML benchmarks
│   └── RESOURCES.md      # External resources
└── README.md             # This file
```

---

## System Requirements

### For CDLI CLI
- Python 3.9+
- ~10MB disk space
- Internet connection for API access

### For Datasets
- SumTablets: ~500MB disk space
- CuneiML: ~50GB for images, ~10MB for metadata only
- MTM24: ~200MB disk space
- Kaggle API credentials (for MTM24)

---

## Roadmap

### Current (v0.1)
- ✅ CDLI CLI tool (production-ready)
- ✅ Unicode cuneiform data
- ✅ Download scripts for major datasets
- ✅ Comprehensive documentation

### Planned
- ORACC corpus integration
- Translation model implementations
- OCR sign detection models
- Preprocessing utilities
- Jupyter notebooks with examples
- Benchmark reproduction scripts
- Data visualization tools

---

## License

- **CDLI CLI:** MIT License
- **Datasets:** Various (see individual licenses in data/README.md)
- **Documentation:** CC BY 4.0
- **Scripts:** MIT License

---

## Acknowledgments

This project builds on:
- CDLI (Cuneiform Digital Library Initiative)
- ORACC (Open Richly Annotated Cuneiform Corpus)
- SumTablets (Simmons & Gordin)
- CuneiML (Taineleau et al.)
- Unicode Consortium

---

## Links

- [CDLI](https://cdli.earth) - Cuneiform Digital Library Initiative
- [ORACC](http://oracc.org) - Open Richly Annotated Cuneiform Corpus
- [SumTablets](https://huggingface.co/datasets/colesimmons/SumTablets) - Hugging Face
- [CuneiML](https://zenodo.org/records/10806319) - Zenodo
- [MTM24](https://www.kaggle.com/datasets/manwithacat/mtm24-akkadian-transliteration) - Kaggle

---

**clayvoices** - Democratizing access to ancient Mesopotamian languages through modern tools and comprehensive datasets.