# Ancient Language Dataset Download Scripts

Automated scripts for downloading major cuneiform datasets.

---

## Available Scripts

| Script | Dataset | Size | Source |
|--------|---------|------|--------|
| `download_sumtablets.py` | SumTablets (91K tablets) | ~500MB | Hugging Face |
| `download_cuneiml.py` | CuneiML (38K photos) | ~50GB | Zenodo |
| `download_mtm24.py` | MTM24 Akkadian (1.15M lines) | ~200MB | Kaggle |

---

## Quick Start

```bash
# Download SumTablets
python download_sumtablets.py

# Download CuneiML (metadata only)
python download_cuneiml.py

# Download CuneiML with images (~50GB)
python download_cuneiml.py --images

# Download MTM24 (requires Kaggle API)
python download_mtm24.py
```

---

## Prerequisites

**For SumTablets:**
```bash
pip install datasets
```

**For CuneiML:**
```bash
pip install httpx
```

**For MTM24:**
```bash
pip install kaggle
# Configure ~/.kaggle/kaggle.json with API credentials
```

---

## Complete Documentation

For detailed information, see:
- **[docs/DATASETS.md](../docs/DATASETS.md)** - Dataset catalog and citations
- **[data/README.md](../data/README.md)** - Data directory overview

---

All datasets will be downloaded to `../data/` by default.
Each script supports `--output` flag to specify custom location.