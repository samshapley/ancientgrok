# Ancient Mesopotamian Languages - Resource Guide

Comprehensive guide to external resources for Sumerian, Akkadian, and cuneiform research.

---

## Online Databases & Corpora

### Primary Sources

| Resource | Focus | URL | Access |
|----------|-------|-----|--------|
| **CDLI** | 500K+ artifacts | https://cdli.earth | Public |
| **ORACC** | Annotated corpus | http://oracc.org | Public |
| **ePSD2** | Sumerian dictionary | http://oracc.museum.upenn.edu/epsd2/ | Public |
| **Archibab** | Akkadian letters | https://www.archibab.fr/ | Public |
| **ARMEP** | Middle East polities | https://www.armep.gwi.uni-muenchen.de | Public |

### CDLI Access

Use the `cdli-cli` tool in this repository:
```bash
cd cdli-cli
pip install -e .
cdli find "your query" --per-page 100
```

See [cdli-cli/README.md](../cdli-cli/README.md) for full documentation.

---

## Dictionaries & Lexicons

### Sumerian

| Resource | Description | Access |
|----------|-------------|--------|
| **ePSD2** | Pennsylvania Sumerian Dictionary | http://oracc.museum.upenn.edu/epsd2/ |
| **ePSD** | Pennsylvania Sumerian Dictionary (v1) | http://psd.museum.upenn.edu/ |
| **Sumerian Lexicon** | John Halloran's lexicon | http://www.sumerian.org/sumerian.pdf |

### Akkadian

| Resource | Description | Access |
|----------|-------------|--------|
| **CAD** | Chicago Assyrian Dictionary (21 vols) | https://oi.uchicago.edu/research/publications/assyrian-dictionary-oriental-institute-university-chicago-cad |
| **AHw** | Akkadisches Handwörterbuch | Library access |
| **CDA** | Concise Dictionary of Akkadian | Purchase |

**Note:** CAD is freely available as PDFs from the Oriental Institute.

---

## Sign Lists & Paleography

### Cuneiform Sign Catalogs

| Resource | Coverage | Format |
|----------|----------|--------|
| **MZL** | Mesopotamian sign list | Print (Borger 2004) |
| **ABZ** | Archaic sign list | Print |
| **LAK** | Early Dynastic signs | Print (Deimel 1922) |
| **Unicode** | Digital standard | See `data/unicode/` in this repo |

### Online Sign References

- **OGSL** (ORACC Global Sign List): http://oracc.org/ogsl
- **aBZL** (Annotated sign list): http://oracc.org/abzl

---

## Learning Resources

### Sumerian

| Resource | Type | Level | URL |
|----------|------|-------|-----|
| **ePSD2 Tutorials** | Online course | Beginner | http://oracc.museum.upenn.edu/epsd2/tutorial |
| **ETCSL** | Literary corpus | Intermediate | http://etcsl.orinst.ox.ac.uk/ |
| **Jagersma Grammar** | Reference | Advanced | Library |

### Akkadian

| Resource | Type | Level | URL |
|----------|------|-------|-----|
| **Huehnergard** | Textbook | Beginner | Purchase |
| **GAG** | Reference grammar | Advanced | Library |
| **Archibab** | Letter corpus | Intermediate | https://www.archibab.fr/ |

---

## Software Tools

### Text Editors & Fonts

| Tool | Purpose | URL |
|------|---------|-----|
| **Emacs CDLI mode** | ATF editing | https://github.com/oracc/emacs-cdli-mode |
| **Cuneiform fonts** | Display Unicode | https://www.hethport.uni-wuerzburg.de/cuneifont/ |
| **Santakku** | Unicode input | https://www.unicode.org/L2/L2021/21190-santakku.pdf |

### Data Processing

| Tool | Purpose | Language | URL |
|------|---------|----------|-----|
| **cdli-cli** | CDLI API access | Python | This repo (`cdli-cli/`) |
| **framework-api-client** | CDLI API (official) | Node.js | https://github.com/cdli-gh/framework-api-client |
| **pyoracc** | ORACC corpus access | Python | https://github.com/oracc/pyoracc |

### Analysis Tools

| Tool | Purpose | URL |
|------|---------|-----|
| **Ur-System** | Sumerian morphology | Research groups |
| **CSEV** | Sign variant analysis | Academic |

---

## Academic Organizations

### International Bodies

- **CDLI** (Cuneiform Digital Library Initiative): https://cdli.earth/about
- **IANES** (International Association for Near Eastern Studies): https://www.ianes.org/
- **IAASSYRIOLOGY** (International Association for Assyriology): https://www.iaassyriology.com/

### Research Institutions

- **Oriental Institute, Chicago**: https://oi.uchicago.edu/
- **British Museum, London**: https://www.britishmuseum.org/
- **Louvre, Paris**: https://www.louvre.fr/
- **Vorderasiatisches Museum, Berlin**: https://www.smb.museum/
- **Yale Babylonian Collection**: https://babylonian-collection.yale.edu/

---

## Journals & Publications

### Open Access

- **CDLJ** (Cuneiform Digital Library Journal): https://cdli.earth/articles/cdlj
- **CDLB** (CDLI Bulletin): https://cdli.earth/articles/cdlb
- **CDLN** (CDLI Notes): https://cdli.earth/articles/cdln

### Major Journals

- Journal of Cuneiform Studies (JCS)
- Zeitschrift für Assyriologie (ZA)
- Revue d'Assyriologie (RA)
- Iraq (British School of Archaeology in Iraq)

---

## Machine Learning Resources

### Datasets (Already in this repo)

- SumTablets: [Hugging Face](https://huggingface.co/datasets/colesimmons/SumTablets)
- CuneiML: [Zenodo](https://zenodo.org/records/10806319)
- MTM24: [Kaggle](https://www.kaggle.com/datasets/manwithacat/mtm24-akkadian-transliteration)

### Models & Code

| Resource | Task | URL |
|----------|------|-----|
| **Akkadian NMT** | Translation | Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC10153418/ |
| **Img2SumGlyphs** | OCR | https://cs231n.stanford.edu/2024/papers/... |
| **AICC** | 130K translations | https://praeclarum.org/2023/06/09/cuneiform.html |

### Competitions

- **Deep Past Initiative**: https://www.kaggle.com/competitions/deep-past-initiative-machine-translation

---

## File Format Documentation

### ATF (ASCII Transliteration Format)

**Official Specification:** http://oracc.museum.upenn.edu/doc/help/editinginatf/primer/

**Structure:**
```
&P123456 = Tablet designation
#atf: lang sux
@tablet
@obverse
1. lugal kur-kur-ra
2. en šul ša3-ga-na
```

### CoNLL-U

**Official Specification:** https://universaldependencies.org/format.html

Used for linguistic annotation of cuneiform texts.

### CDLI Metadata Schema

**Official Specification:** https://cdli.earth/pages/schema/1.0

JSON-based schema for artifact metadata.

---

## Unicode & Encoding

### Cuneiform Unicode Blocks

| Block | Range | Characters | Fonts |
|-------|-------|------------|-------|
| Cuneiform | U+12000–U+123FF | 922 | [CuneiformOB](http://www.hethport.uni-wuerzburg.de/cuneifont/) |
| Cuneiform Numbers | U+12400–U+1247F | 116 | Same |
| Early Dynastic | U+12480–U+1254F | 196 | Same |

### Font Resources

- **Free Fonts:** http://www.hethport.uni-wuerzburg.de/cuneifont/
- **Noto Sans Cuneiform:** https://fonts.google.com/noto/specimen/Noto+Sans+Cuneiform

---

## Research Tutorials

### Getting Started with Cuneiform

1. **Learn Sumerian:**
   - Start with ePSD2 tutorial: http://oracc.museum.upenn.edu/epsd2/tutorial
   - Read ETCSL texts: http://etcsl.orinst.ox.ac.uk/

2. **Learn Akkadian:**
   - Huehnergard's "Grammar of Akkadian" (textbook)
   - Practice with Archibab letters: https://www.archibab.fr/

3. **Learn to Read Tablets:**
   - Install cuneiform fonts
   - Practice with CDLI images: Use `cdli-cli` to download examples
   - Compare photos with line art tracings

### Using the Data

1. **Download a dataset:**
   ```bash
   cd scripts
   python download_sumtablets.py
   ```

2. **Explore the data:**
   ```python
   from datasets import load_from_disk
   ds = load_from_disk("../data/sumtablets")
   print(ds['train'][0])
   ```

3. **Build something:**
   - Train a transliteration model
   - Create sign frequency analysis
   - Visualize text distributions

---

## Online Communities

- **CDLI Forum**: Contact via cdli-support@ames.ox.ac.uk
- **ORACC Mailing List**: http://oracc.org/doc/help/mailinglists/
- **Reddit r/Cuneiform**: https://www.reddit.com/r/cuneiform/
- **Twitter #Assyriology**: Academic discussions

---

## Workshops & Conferences

### Regular Events

- **Rencontre Assyriologique Internationale (RAI)** - Annual
- **American Oriental Society (AOS)** - Annual
- **CDLI Workshops** - Periodic

### Online Resources

- **CDLI Webinars**: Check https://cdli.earth for announcements
- **ORACC Documentation**: http://oracc.org/doc/

---

## Recommended Reading

### Introductory

- Oppenheim, "Ancient Mesopotamia" (1964) - Classic introduction
- Michalowski, "Sumerian" (2004) - Language overview
- Huehnergard, "Grammar of Akkadian" (2011) - Akkadian primer

### Reference

- Borger, "Mesopotamisches Zeichenlexikon" (MZL) - Sign list
- CAD (Chicago Assyrian Dictionary) - Complete dictionary
- Jagersma, "Grammar of Sumerian" - Comprehensive grammar

### Digital Humanities

- Chiarcos et al. (2018) - Linked Open Data for Sumerian
- Gutherz et al. (2023) - Neural MT for Akkadian
- Pagé-Perron et al. - CDLI development papers

---

## Contributing to this Resource Guide

Know of a useful resource not listed here?

1. Check it's relevant (ancient Mesopotamian languages)
2. Verify it's accessible (working URL)
3. Add to appropriate section with description
4. Submit pull request

---

## Version History

- **January 2026:** Initial resource compilation
- URLs verified: January 16, 2026

---

Last updated: January 16, 2026