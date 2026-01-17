# CDLI CLI Usage Guide

Complete guide to using the Cuneiform Digital Library Initiative command-line interface.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Command Reference](#command-reference)
5. [Practical Examples](#practical-examples)
6. [Python API](#python-api)
7. [Troubleshooting](#troubleshooting)

---

## Installation

```bash
# Install from PyPI (when published)
pip install cdli-cli

# Or install from source
git clone https://github.com/cdli-cli/cdli-cli.git
cd cdli-cli
pip install -e .
```

**Requirements:** Python 3.9+

---

## Quick Start

```bash
# Search for tablets
cdli find "Ur III"

# Get help
cdli --help
cdli get --help
cdli search --help
```

---

## Core Concepts

### Entity Types

CDLI organizes data into entity types:

| Entity | What It Represents |
|--------|--------------------|
| **Tablet** | Cuneiform tablets (artifacts with inscriptions) |
| **Artifact** | Physical objects (tablets, seals, etc.) |
| **Inscription** | Text content of tablets |
| **Publication** | Academic publications referencing artifacts |
| **Collection** | Museums and institutions holding artifacts |
| **Period** | Historical periods (Ur III, Old Babylonian, etc.) |
| **Provenance** | Find locations (Uruk, Nippur, etc.) |
| **Genre** | Text types (administrative, literary, etc.) |
| **Language** | Languages (Sumerian, Akkadian, etc.) |
| **Material** | Materials (clay, stone, etc.) |

### Data Formats

The CLI supports all CDLI API formats:

**Metadata:** JSON, JSON-LD, RDF/XML, Turtle, N-Triples
**Inscriptions:** C-ATF, CDLI-CoNLL, CoNLL-U  
**Bibliographies:** BibTeX, RIS, CSL-JSON, formatted text
**Tabular:** CSV, TSV, Excel

---

## Command Reference

### Global Options

All commands support:
- `--output, -o FILE` - Save to file instead of stdout
- `--base-url, -b URL` - Override CDLI API base URL
- `--help` - Show command help

### Search Commands

#### Basic Search

```bash
cdli find QUERY [OPTIONS]

# Examples
cdli find "administrative"
cdli find "Ur III"
cdli find "royal inscription" --per-page 50
cdli find "Sumerian" --page 2 --output results.json
```

#### Advanced Search

```bash
cdli search advanced [FILTERS] [OPTIONS]

# Filters
--designation TEXT    # Tablet designation
--period TEXT        # Historical period
--provenance TEXT    # Find location
--genre TEXT         # Text genre
--language TEXT      # Language
--collection TEXT    # Collection name
--material TEXT      # Material type
--inscription TEXT   # Inscription content

# Examples
cdli search advanced --period "Ur III" --language "Sumerian"
cdli search advanced --genre "Administrative" --provenance "Girsu"
cdli search advanced --inscription "lugal"
```

### Get Commands

Retrieve individual entities:

```bash
cdli get tablet ID [OPTIONS]
cdli get artifact ID [OPTIONS]
cdli get publication ID [OPTIONS]
cdli get collection ID [OPTIONS]
cdli get period ID [OPTIONS]
cdli get provenance ID [OPTIONS]
cdli get genre ID [OPTIONS]
cdli get language ID [OPTIONS]
cdli get material ID [OPTIONS]

# Get multiple tablets at once
cdli get ids P000001 P000002 P000003

# Format options
--format json        # JSON (default)
--format jsonld      # JSON-LD (Linked Data)
--format turtle      # Turtle RDF
--format rdf         # RDF/XML
--format ntriples    # N-Triples

# Examples
cdli get tablet P000001
cdli get tablet P000001 --format turtle --output P000001.ttl
cdli get artifact 12345 --format jsonld
cdli get collection 1 --output vorderasiatisches_museum.json
```

### Inscription Commands

```bash
cdli get inscription ID [OPTIONS]

# Formats
--format atf      # C-ATF (Canonical ATF) - default
--format conll    # CDLI-CoNLL
--format conllu   # CoNLL-U

# Examples
cdli inscription P000001
cdli inscription P000001 --format atf --output P000001.atf
cdli inscription P000001 --format conll
```

### List Commands

```bash
cdli list tablets [OPTIONS]
cdli list collections [OPTIONS]
cdli list periods [OPTIONS]
cdli list genres [OPTIONS]
cdli list languages [OPTIONS]
cdli list provenances [OPTIONS]

# Pagination
--page, -p NUM       # Page number (default: 1)
--per-page, -n NUM   # Results per page (default: 25)

# Examples
cdli list periods
cdli list collections --per-page 50
cdli list languages --page 2 --output languages.json
```

### Export Commands

```bash
cdli export tablets [OPTIONS]
cdli export publications [OPTIONS]

# Formats
--format csv    # CSV (default)
--format tsv    # TSV
--format xlsx   # Excel

# Examples
cdli export tablets --output tablets.csv
cdli export tablets --format xlsx --page 1 --per-page 1000
cdli export publications --output pubs.tsv --format tsv
```

### Bibliography Commands

```bash
cdli bib tablet ID [OPTIONS]
cdli bib publication ID [OPTIONS]

# Formats
--format bibtex      # BibTeX (default)
--format ris         # RIS
--format csljson     # CSL-JSON
--format formatted   # Formatted text

# CSL styles (for formatted output)
--style apa
--style chicago-author-date
--style mla
# See https://github.com/citation-style-language/styles for full list

# Examples
cdli bib tablet P000001
cdli bib tablet P000001 --format ris --output P000001.ris
cdli bib publication 123 --format formatted --style apa
```

---

## Practical Examples

### Research Workflow: Studying Ur III Administrative Texts

```bash
# 1. Search for Ur III administrative texts
cdli find "Ur III administrative" --per-page 100 --output ur3_admin.json

# 2. Extract tablet IDs
python3 << 'EOF'
import json
with open('ur3_admin.json') as f:
    data = json.load(f)
    for tablet in data['results'][:10]:
        print(f"{tablet.get('designation', 'N/A')}: {tablet.get('museum_no', 'N/A')}")
EOF

# 3. Get detailed metadata for specific tablets
cdli get tablet P123456 --output P123456_full.json

# 4. Get inscription text
cdli inscription P123456 --format atf --output P123456.atf

# 5. Export bibliography
cdli bib tablet P123456 --output P123456.bib
```

### Bulk Data Collection

```bash
#!/bin/bash
# Download tablets in batches
for page in {1..10}; do
    echo "Fetching page $page..."
    cdli export tablets \
        --page $page \
        --per-page 1000 \
        --output "data/tablets_p${page}.csv"
    sleep 2  # Be nice to the API
done
```

### Building a Linked Data Graph

```bash
# Get tablets as Turtle RDF for SPARQL
cdli find "royal inscription" --per-page 20 --output results.json

# Convert each to Turtle
python3 << 'EOF'
import json
import subprocess

with open('results.json') as f:
    tablets = json.load(f)['results']

for tablet in tablets[:5]:
    tablet_id = tablet.get('designation', '').split(',')[0]
    if tablet_id.startswith('P'):
        try:
            subprocess.run([
                'cdli', 'get', 'tablet', tablet_id,
                '--format', 'turtle',
                '--output', f'{tablet_id}.ttl'
            ])
        except:
            print(f"Skipped {tablet_id}")
EOF

# Merge all Turtle files
cat *.ttl > combined_graph.ttl
```

### Citation Management

```bash
# Build bibliography for a research paper
cdli find "Sumerian literature" --per-page 50 --output lit_search.json

# Extract citations
python3 << 'EOF'
import json
import subprocess

with open('lit_search.json') as f:
    tablets = json.load(f)['results']

with open('references.bib', 'w') as out:
    for tablet in tablets[:20]:
        tablet_id = tablet.get('designation', '').split(',')[0]
        if tablet_id.startswith('P'):
            try:
                result = subprocess.run(
                    ['cdli', 'bib', 'tablet', tablet_id],
                    capture_output=True,
                    text=True
                )
                out.write(result.stdout + '\n')
            except:
                pass
EOF
```

---

## Python API

### Basic Usage

```python
from cdli_cli.client import CDLIClient
from cdli_cli.models import OutputFormat, InscriptionFormat

# Context manager (recommended)
with CDLIClient() as client:
    results = client.search("Uruk", per_page=10)
    print(f"Found {results.total} tablets")

# Manual management
client = CDLIClient()
try:
    tablet = client.get_tablet("P000001")
finally:
    client.close()
```

### Search Examples

```python
# Simple search
results = client.search("administrative text", page=1, per_page=50)
for tablet in results.results:
    print(tablet['designation'])

# Advanced search
results = client.advanced_search(
    period="Ur III",
    language="Sumerian",
    genre="Administrative",
    provenance="Girsu"
)

# Search with pagination
all_results = []
for page in range(1, 11):
    results = client.search("Akkadian", page=page, per_page=100)
    all_results.extend(results.results)
```

### Getting Data

```python
# Get tablet in different formats
json_data = client.get_tablet("P000001", OutputFormat.JSON)
turtle_data = client.get_tablet("P000001", OutputFormat.TURTLE)

# Get inscription
atf_text = client.get_inscription("P000001", InscriptionFormat.ATF)

# Get bibliography
bibtex = client.get_tablet_bibliography("P000001")
```

### Exports

```python
from cdli_cli.models import TabularFormat

# Export to CSV
csv_data = client.export_tablets(TabularFormat.CSV, page=1, per_page=1000)

# Save to file
from pathlib import Path
output = Path("tablets.csv")
client.save_output(csv_data, output, "csv")
```

---

## Troubleshooting

### Common Issues

#### "API Error (500)"

This is an upstream CDLI API issue. Some endpoints return server errors:
- Try a different tablet ID
- Check if the endpoint is functioning at cdli.earth
- File an issue with CDLI if persistent

#### "Not found"

- Verify the ID format (P-numbers for tablets, Q for composites, S for seals)
- Some IDs may not exist in the database
- Try searching first to find valid IDs

#### Empty Results

- Check your search query spelling
- Try broader search terms
- Use `--per-page 100` to get more results

### Getting Help

```bash
# General help
cdli --help

# Command-specific help
cdli get --help
cdli search --help
cdli export --help

# Sub-command help
cdli get tablet --help
cdli search advanced --help
```

### Debug Mode

```python
# Enable httpx logging for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

from cdli_cli.client import CDLIClient
with CDLIClient() as client:
    client.search("test")
```

---

## Advanced Features

### Custom Base URL

```bash
# Use a different CDLI instance
cdli find "test" --base-url https://test.cdli.earth
```

### Piping and Processing

```bash
# Pipe to jq for JSON processing
cdli find "Sumerian" --per-page 10 | jq '.results[] | .designation'

# Combine with other tools
cdli find "administrative" --per-page 1000 -o data.json
python analyze_tablets.py data.json
```

### Batch Processing

```bash
# Process multiple queries
for query in "administrative" "literary" "legal"; do
    cdli find "$query" --per-page 100 -o "${query}_tablets.json"
done
```

---

## Best Practices

1. **Use pagination** - Don't request too many results at once
2. **Save to files** - Use `--output` for large datasets
3. **Check format** - Use appropriate format for your use case
4. **Handle errors** - CDLI API may have intermittent issues
5. **Rate limiting** - Be respectful, add delays between bulk requests

---

## Resources

- [CDLI Website](https://cdli.earth)
- [CDLI API Documentation](https://cdli.earth/docs/api)
- [C-ATF Format](http://oracc.museum.upenn.edu/doc/help/editinginatf/primer/)
- [CoNLL-U Format](https://universaldependencies.org/format.html)
- [CSL Styles](https://github.com/citation-style-language/styles)

---

## Contributing

Found a bug? Want to add features?

1. Check existing issues
2. Create a detailed bug report or feature request
3. Submit a pull request with tests

---

## License

MIT License - see [LICENSE](../LICENSE) for details.