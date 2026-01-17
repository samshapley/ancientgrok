# CDLI CLI

A command-line interface for the [Cuneiform Digital Library Initiative (CDLI)](https://cdli.earth) API.

Access over 500,000 cuneiform artifacts, inscriptions, publications, and metadata directly from your terminal.

## Installation

```bash
pip install cdli-cli
```

Or install from source:

```bash
git clone https://github.com/cdli-cli/cdli-cli.git
cd cdli-cli
pip install -e .
```

## Quick Start

```bash
# Search for tablets (WORKING)
cdli find "Ur III"

# Download tablet images (WORKING)
cdli image photo P000001
cdli image both P000001  # Download both photo and lineart

# List metadata (WORKING)
cdli list periods
cdli list collections
cdli list languages

# Export tablets to CSV (WORKING)
cdli export tablets --output tablets.csv

# Get help
cdli --help
```

**Note:** Some CDLI API endpoints return 500 errors (individual tablet retrieval, advanced search, inscription fetching). These are upstream API issues, not client bugs. Basic search, listing, and image downloads work perfectly.

## Commands

### Get Commands

Retrieve individual entities by ID:

```bash
# ⚠️ Note: Some individual artifact endpoints return 500 errors (upstream API issue)
# Get tablet metadata (JSON by default) 
cdli get tablet P000001  # May return 500 error

# Get in different formats
cdli get tablet P000001 --format jsonld    # JSON-LD (Linked Data)
cdli get tablet P000001 --format turtle    # Turtle RDF
cdli get tablet P000001 --format rdf       # RDF/XML

# Get other entity types
cdli get artifact <id>     # May return 500 error
cdli get publication <id>
cdli get collection <id>
cdli get period <id>
cdli get provenance <id>
cdli get genre <id>
cdli get language <id>
cdli get material <id>

# Get multiple tablets at once (URL ID query)
cdli get ids P000001 P000002 P000003

# ⚠️ Get inscription text - May return 500 errors (upstream API issue)
cdli get inscription P000001 --format atf     # C-ATF format
cdli get inscription P000001 --format conll   # CDLI-CoNLL
cdli get inscription P000001 --format conllu  # CoNLL-U
```

### List Commands

List entities with pagination:

```bash
cdli list tablets --page 1 --per-page 50
cdli list collections
cdli list periods
cdli list genres
cdli list languages
cdli list provenances
```

### Search Commands

```bash
# ✅ Simple search (WORKING)
cdli search query "royal inscription"

# ⚠️ Advanced search - Returns 500 errors (upstream API issue)
cdli search advanced \
    --period "Ur III" \
    --language "Sumerian" \
    --genre "Administrative" \
    --provenance "Girsu"

# Use simple search with keywords instead:
cdli find "Ur III Sumerian Administrative"
```

### Image Commands

Download tablet photographs and line art drawings:

```bash
# Download full-resolution photograph
cdli image photo P000001

# Download lineart (hand-drawn tracing)
cdli image lineart P000001

# Download both photo and lineart
cdli image both P000001

# Download thumbnails instead
cdli image photo P000001 --thumbnail
cdli image lineart P000001 -t

# Specify output path
cdli image photo P000001 --output tablets/P000001_photo.jpg
```

**Image Types:**
- **Photo**: High-resolution photograph of the tablet (typically 300 DPI, ~300KB)
- **Lineart**: Hand-drawn tracing emphasizing sign boundaries (~50-100KB)

**Note:** Images follow predictable URLs at `cdli.earth/dl/photo/{P-number}.jpg` and `cdli.earth/dl/lineart/{P-number}_l.jpg`. Not all tablets have lineart available.

### Export Commands

Export data in tabular formats:

```bash
# Export to CSV (default)
cdli export tablets --output tablets.csv

# Export to TSV
cdli export tablets --format tsv --output tablets.tsv

# Export to Excel
cdli export tablets --format xlsx --output tablets.xlsx

# Export publications
cdli export publications --output pubs.csv

# Paginated export
cdli export tablets --page 1 --per-page 1000 --output tablets_p1.csv
```

### Bibliography Commands

Get bibliographic references:

```bash
# BibTeX format (default)
cdli bib tablet P000001

# RIS format
cdli bib tablet P000001 --format ris

# CSL-JSON
cdli bib publication <id> --format csljson

# Formatted bibliography with style
cdli bib tablet P000001 --format formatted --style apa
cdli bib tablet P000001 --format formatted --style chicago-author-date
```

## Output Options

All commands support:

- `--output, -o`: Save to file instead of stdout
- `--format, -f`: Specify output format
- `--base-url, -b`: Override CDLI API base URL

## Supported Formats

### Metadata Formats
| Format | Description | Extension |
|--------|-------------|-----------|
| `json` | JSON (default) | .json |
| `jsonld` | JSON-LD (Linked Data) | .jsonld |
| `rdf` | RDF/XML | .rdf |
| `turtle` | Turtle | .ttl |
| `ntriples` | N-Triples | .nt |

### Inscription Formats
| Format | Description |
|--------|-------------|
| `atf` | C-ATF (Canonical ATF) |
| `conll` | CDLI-CoNLL |
| `conllu` | CoNLL-U |

### Bibliography Formats
| Format | Description |
|--------|-------------|
| `bibtex` | BibTeX |
| `ris` | RIS |
| `csljson` | CSL-JSON |
| `formatted` | Formatted text (use with --style) |

### Tabular Formats
| Format | Description | Extension |
|--------|-------------|-----------|
| `csv` | Comma-separated | .csv |
| `tsv` | Tab-separated | .tsv |
| `xlsx` | Excel | .xlsx |

## API Endpoint Status

| Feature | Status | Notes |
|---------|--------|-------|
| Basic search (`cdli find`) | ✅ Working | Returns 25+ results per query |
| List metadata (periods, collections, etc.) | ✅ Working | All list commands functional |
| Export to CSV/TSV/XLSX | ✅ Working | Tabular exports functional |
| **Image downloads** | ✅ Working | Photos and lineart via predictable URLs |
| URL ID query | ✅ Working | Batch fetch by P/Q/S numbers |
| **Individual tablet retrieval** | ⚠️ Upstream 500 error | CDLI API issue |
| **Advanced search** | ⚠️ Upstream 500 error | CDLI API issue |
| **Inscription fetching** | ⚠️ Upstream 500 error | CDLI API issue |

The CLI correctly implements the CDLI API specification. Errors are server-side issues.

## Examples

### Research Workflow

```bash
# 1. Search for tablets from Ur III period (WORKING)
cdli find "Ur III administrative" --per-page 100 -o ur3_admin.json

# 2. Download images for the first 10 results
python3 << 'EOF'
import json
import subprocess

with open('ur3_admin.json') as f:
    data = json.load(f)
    for tablet in data['results'][:10]:
        designation = tablet.get('designation', '')
        if 'P' in designation:
            p_num = [p for p in designation.split() if p.startswith('P')][0]
            print(f"Downloading {p_num}...")
            subprocess.run(['cdli', 'image', 'both', p_num])
EOF

# 3. Analyze the search results
python3 << 'EOF'
import json
with open('ur3_admin.json') as f:
    data = json.load(f)
    print(f"Found {data['total']} tablets")
    for tablet in data['results'][:10]:
        print(f"{tablet.get('designation', 'N/A')}: {tablet.get('museum_no', 'N/A')}")
EOF

# 4. List available periods (WORKING)
cdli list periods -o periods.json

# 5. List languages (WORKING)
cdli list languages -o languages.json
```

### Bulk Data Collection

```bash
# Export first 10,000 tablets across pages
for i in {1..100}; do
    cdli export tablets --page $i --per-page 100 -o tablets_p${i}.csv
done
```

### Linked Data Export

```bash
# Get tablet as Turtle for SPARQL processing
cdli get tablet P000001 --format turtle

# Get as JSON-LD for JSON-LD framing
cdli get tablet P000001 --format jsonld -o tablet.jsonld
```

## Python API

You can also use the client directly in Python:

```python
from cdli_cli.client import CDLIClient
from cdli_cli.models import OutputFormat, InscriptionFormat
from pathlib import Path

with CDLIClient() as client:
    # Get tablet metadata
    tablet = client.get_tablet("P000001")
    print(tablet)
    
    # Download images
    photo = client.download_image("P000001", "photo")
    lineart = client.download_image("P000001", "lineart")
    print(f"Downloaded: {photo}, {lineart}")
    
    # Get inscription
    inscription = client.get_inscription("P000001", InscriptionFormat.ATF)
    print(inscription)
    
    # Search
    results = client.search("Ur III administrative", page=1, per_page=50)
    print(f"Found {results.total} results")
    
    # Advanced search
    results = client.advanced_search(
        period="Ur III",
        language="Sumerian",
        genre="Administrative"
    )
    
    # Export
    csv_data = client.export_tablets()
```

## Entity Types

| Entity | Description |
|--------|-------------|
| `tablet` / `cdli-tablet` | Cuneiform tablets (primary artifacts) |
| `artifact` | General artifacts |
| `publication` | Academic publications |
| `inscription` | Text content of tablets |
| `collection` | Museum collections |
| `period` | Historical periods |
| `genre` | Text genres (administrative, literary, etc.) |
| `language` | Languages (Sumerian, Akkadian, etc.) |
| `provenance` | Find locations |
| `material` | Materials (clay, stone, etc.) |

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [CDLI Website](https://cdli.earth)
- [CDLI API Documentation](https://cdli.earth/docs/api)
- [CDLI on GitHub](https://github.com/cdli-gh)