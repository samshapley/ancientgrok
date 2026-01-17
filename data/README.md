# Ancient Language Datasets

This directory contains datasets for ancient Mesopotamian languages.

---

## Directory Structure

```
data/
├── unicode/          # ✅ Unicode cuneiform characters (1,205 signs, 3MB)
├── sumtablets/       # ⏳ Download with scripts/download_sumtablets.py
├── cuneiml/          # ⏳ Download with scripts/download_cuneiml.py
├── mtm24/            # ⏳ Download with scripts/download_mtm24.py
└── cdli/             # User-created exports from cdli-cli
```

---

## What's Included

### Unicode Cuneiform (Hardcoded - 3MB)
- 1,205 Unicode cuneiform characters with names
- Complete sign list for U+12000–U+1254F ranges
- Ready to use - already in repository

### External Datasets (Download Required)

| Dataset | Size | Download Script |
|---------|------|-----------------|
| **SumTablets** | ~500MB | `scripts/download_sumtablets.py` |
| **CuneiML** | ~50GB | `scripts/download_cuneiml.py` |
| **MTM24 Akkadian** | ~200MB | `scripts/download_mtm24.py` |
| **CDLI Exports** | On-demand | Use `cdli-cli` tool |

---

## Quick Start

**To download a dataset:**
```bash
cd ../scripts
python download_sumtablets.py  # Downloads to data/sumtablets/
```

**To export CDLI data:**
```bash
cd ../cdli-cli
pip install -e .
cdli find "Ur III" --per-page 1000 -o ../data/cdli/ur3.json
```

---

## Complete Documentation

For comprehensive dataset information, see:
- **[docs/DATASETS.md](../docs/DATASETS.md)** - Complete dataset catalog
- **[scripts/README.md](../scripts/README.md)** - Download instructions
- **[docs/BENCHMARKS.md](../docs/BENCHMARKS.md)** - ML model performance

---

**Note:** Large datasets are gitignored. Only Unicode cuneiform data (~3MB) is tracked in git.