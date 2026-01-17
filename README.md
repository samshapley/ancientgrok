# AncientGrok

Interactive CLI agent for ancient world knowledge, powered by Grok AI with agentic research capabilities, integrated CDLI database, Open Context archaeological data, image generation, research report compilation, and academic paper download.

```
 ▗▄▖ ▗▖  ▗▖ ▗▄▄▖▗▄▄▄▖▗▄▄▄▖▗▖  ▗▖▗▄▄▄▖▗▄▄▖▗▄▄▖  ▗▄▖ ▗▖ ▗▖
▐▌ ▐▌▐▛▚▖▐▌▐▌     █  ▐▌   ▐▛▚▖▐▌  █ ▐▌   ▐▌ ▐▌▐▌ ▐▌▐▌▗▞▘
▐▛▀▜▌▐▌ ▝▜▌▐▌     █  ▐▛▀▀▘▐▌ ▝▜▌  █ ▐▌▝▜▌▐▛▀▚▖▐▌ ▐▌▐▛▚▖ 
▐▌ ▐▌▐▌  ▐▌▝▚▄▄▖▗▄█▄▖▐▙▄▄▖▐▌  ▐▌  █ ▝▚▄▞▘▐▌ ▐▌▝▚▄▞▘▐▌ ▐▌

Ancient World Knowledge Agent
Powered by Grok AI • 18 Agentic Tools • Research & Visualization
```

---

## What is AncientGrok?

AncientGrok is a production-ready terminal-based research assistant that combines conversational AI with real database access, enabling scholars and enthusiasts to:

- **Search 500,000+ cuneiform tablets** in the CDLI database
- **Access 147,000+ archaeological records** from Open Context with detailed measurements
- **Filter 1,205 cuneiform signs** by name pattern from Unicode database
- **Download academic papers** from arXiv, JSTOR, institutional repositories
- **Generate historical visualizations** using Grok Imagine
- **Create research reports** compiled to PDF with LaTeX
- **Analyze tablet images** using AI vision
- **Track research costs** with real-time per-turn and session totals

All through natural conversation with an AI that understands ancient history.

---

## Installation

### Prerequisites

- Python 3.9+
- xAI API key ([Get one here](https://console.x.ai/))
- LaTeX distribution (for PDF reports)

### Quick Install

```bash
cd ancientgrok
pip install -e .

# Install CDLI CLI dependency
cd ../clayvoices/cdli-cli
pip install -e .

# Set API key
export XAI_API_KEY="your-xai-api-key"

# Launch
ancientgrok
```

See [SETUP.md](SETUP.md) for complete installation instructions.

---

## Features

### 18 Integrated Tools

**Server-Side Agentic Tools (3):**
- 🌐 **web_search** - Find scholarly resources and current research
- 🐦 **x_search** - Search X/Twitter for academic discussions
- 💻 **code_execution** - Python computational analysis

**Client-Side CDLI Tools (5):**
- 🔍 **search_cdli** - Search 500,000+ cuneiform tablets
- 📜 **get_tablet_details** - Complete metadata for P-numbers
- 🖼️ **download_tablet_image** - High-res photos and linearts
- 📅 **list_periods** - All 32 historical periods
- 🏛️ **list_collections** - 100+ museums worldwide

**Client-Side Open Context Tools (3):**
- 🏺 **search_open_context** - Search 147K+ archaeological records
- 📊 **get_opencontext_attributes** - Discover data attributes
- 🔬 **get_detailed_opencontext_records** - Get comprehensive artifact data with measurements, classifications, taxonomic IDs

**Client-Side Cuneiform Reference (2):**
- 📖 **lookup_cuneiform_sign** - Query 1,205 Unicode signs
- 📚 **list_cuneiform_signs** - Browse and filter signs by name pattern

**Client-Side Vision Tools (1):**
- 👁️ **view_analyze_image** - Analyze tablet photos and images

**Client-Side Paper Tools (1):**
- 📥 **download_paper** - Download academic PDFs (auto-opens)

**Client-Side Creative Tools (2):**
- 🎨 **generate_image** - Grok Imagine visualizations (auto-opens)
- 📝 **create_research_report** - LaTeX to PDF (auto-opens)

**Client-Side Media Tools (1):**
- ✏️ **edit_image** - Modify generated or downloaded images

---

## Verified Capabilities

**Database Access:**
- ✅ 500,000+ CDLI cuneiform tablets
- ✅ 147,958 Çatalhöyük archaeological records (with detailed measurements)
- ✅ 879 Troy excavation records
- ✅ 45 Göbekli Tepe records
- ✅ 16 Hattusa records
- ✅ 1,205 Unicode cuneiform signs (filterable by name pattern)

**Content Generation:**
- ✅ 9 images generated (4MB total)
- ✅ 3 research reports compiled (1.1MB total, including 902KB scholarly study)
- ✅ 5 CDLI tablets downloaded (7.7MB high-res images)
- ✅ 1 academic paper downloaded (1.1MB PDF from arXiv)

**Multi-Tool Orchestration:**
- ✅ Cuneiform lookup + Image generation + Report compilation
- ✅ CDLI search + Image download + Vision analysis
- ✅ Open Context search + Detailed records + Measurements analysis
- ✅ Paper download + Research synthesis

**UI Features:**
- ✅ Rich table formatting for all tool arguments
- ✅ Real-time cost tracking (per-turn + session total)
- ✅ Incremental streaming responses
- ✅ Yellow/blue professional theme
- ✅ Auto-open for generated content
- ✅ Clean visual hierarchy with section dividers

---

## Example Usage

### Database Queries with Filtering
```
You: List cuneiform signs containing 'KING'

🔧 list_cuneiform_signs
 Parameter     Value
 name_filter   KING
 limit         50

Returns: LUGAL (U+12217, 𒈗) and variants with Unicode characters
```

### Detailed Archaeological Data
```
You: Get detailed artifact measurements from Çatalhöyük

🔧 search_open_context
 Parameter  Value
 query      Çatalhöyük

🔧 get_detailed_opencontext_records
 Parameter    Value
 url          [search URL]
 max_records  10

Returns: Bone measurements (GL, BT), classifications, use-wear analysis
```

### Complete Research Workflow
```
You: Create a comprehensive report on cuneiform sign A

Agent orchestrates:
1. lookup_cuneiform_sign → Find sign in database
2. search_cdli → Find tablets with the sign
3. generate_image → Create evolution diagram
4. create_research_report → Compile 16-page PDF

Result: 902KB scholarly document with embedded images, bibliography
Tools: search_cdli: 3x, generate_image: 2x, create_research_report: 1x
Cost: $0.0234 | Session: $0.0234
```

---

## Commands

- `help` - Show commands and examples
- `tools` - Display all 18 tools
- `clear` - Clear screen
- `exit` / `quit` - Exit (shows session cost summary)

---

## Production Features

**Polished UI:**
- Yellow/blue professional color theme
- Rich tables for all tool arguments
- Clean section dividers between turns
- Graceful empty parameter handling ("No parameters" instead of {})
- Proper visual hierarchy and spacing

**Cost Transparency:**
- Real-time tracking using Grok pricing ($0.20 input, $0.50 output per 1M tokens)
- Per-turn cost display after each response
- Cumulative session total
- Final summary on exit

**Auto-Open Functionality:**
- Generated images open automatically in default viewer
- Research reports (PDFs) open automatically
- Downloaded papers open automatically
- Seamless workflow for content creation

---

## Technical Details

**Model:** grok-4-1-fast-non-reasoning (default)
- 2M token context window
- ~2-3s response time
- Autonomous tool selection
- Incremental streaming

**Dependencies:** All managed via requirements.txt
- xai-sdk (Grok API)
- cdli-cli (CDLI database)
- httpx (HTTP requests)
- rich (Terminal UI)
- pandas, numpy (Open Context)
- typer, prompt-toolkit (CLI)

**Costs:**
- Server-side tools: $5 per 1,000 calls
- Client-side tools: Free
- Token usage: $0.20 input, $0.50 output per 1M tokens
- Typical turn: $0.01-0.03

---

## Testing

All 18 tools comprehensively tested and verified:

- ✅ All CDLI tools functional
- ✅ Open Context integration verified (detailed records working)
- ✅ Cuneiform filtering tested (name pattern matching)
- ✅ Vision analysis working
- ✅ Image generation creates quality visualizations
- ✅ Research reports compile to professional PDFs
- ✅ Paper download verified
- ✅ Cost tracking accurate
- ✅ Multi-tool orchestration demonstrated

See [TESTING.md](TESTING.md) for complete evidence.

---

## Documentation

- [README.md](README.md) - This file
- [SETUP.md](SETUP.md) - Complete installation guide
- [FEATURES.md](FEATURES.md) - Feature catalog with testing evidence
- [TESTING.md](TESTING.md) - Test documentation
- [FUTURE_TOOLS.md](FUTURE_TOOLS.md) - Enhancement roadmap

---

## License

MIT License

---

## Acknowledgments

- **xAI Grok** - AI with 2M context and agentic capabilities
- **CDLI** - Cuneiform Digital Library Initiative
- **Open Context** - Archaeological data platform
- **cdli-cli** - Python CDLI client
- **Rich** - Terminal UI library

---

**AncientGrok** - Democratizing ancient world research through conversational AI with real database integration, scholarly paper access, and professional document generation.
