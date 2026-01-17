# AncientGrok Setup Guide

Complete installation and configuration instructions for AncientGrok.

---

## Prerequisites

Before installing AncientGrok, ensure you have:

### 1. Python 3.9 or Higher

Check your Python version:
```bash
python3 --version
```

If Python is not installed or too old:
- **Fedora/RHEL:** `sudo dnf install python3.9`
- **Ubuntu/Debian:** `sudo apt-get install python3.9`
- **macOS:** `brew install python@3.9`

### 2. xAI API Key

1. Visit https://console.x.ai/
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create New Key"
5. Copy your key (starts with `xai-`)
6. Store it securely

**Cost:** $25 free credits for new users, then pay-as-you-go ($0.20-$0.50 per 1M tokens)

### 3. LaTeX Distribution (For PDF Reports)

**Fedora/RHEL:**
```bash
sudo dnf install -y texlive-scheme-basic
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y texlive-latex-base texlive-latex-extra
```

**macOS:**
```bash
brew install --cask mactex-no-gui
```

**Verify:**
```bash
pdflatex --version
```

---

## Installation

### Step 1: Clone or Download Repository

If you have the clayvoices repository:
```bash
cd /path/to/clayvoices
```

Or download ancientgrok separately if provided as standalone.

### Step 2: Install CDLI CLI

AncientGrok requires the CDLI command-line client:

```bash
cd clayvoices/cdli-cli
pip install -e .
```

**Verify:**
```bash
cdli --version
```

### Step 3: Install AncientGrok

```bash
cd ../ancientgrok
pip install -e .
```

This installs:
- xai-sdk (Grok API client)
- httpx (HTTP requests)
- rich (Terminal UI)
- typer, prompt-toolkit (CLI framework)
- pandas, numpy (Open Context data)
- python-slugify, requests (utilities)

**Verify:**
```bash
ancientgrok --help
```

Should show AncientGrok command information.

---

## Configuration

### Set API Key

**Method 1: Environment Variable (Recommended)**

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export XAI_API_KEY="xai-your-actual-key-here"
```

Then reload:
```bash
source ~/.bashrc
```

**Method 2: Per-Session**

```bash
export XAI_API_KEY="xai-your-actual-key-here"
ancientgrok
```

**Verify:**
```bash
echo $XAI_API_KEY
```

Should show your key (starting with `xai-`).

---

## First Run

### Launch AncientGrok

```bash
ancientgrok
```

You should see:
```
 ▗▄▖ ▗▖  ▗▖ ▗▄▄▖▗▄▄▄▖▗▄▄▄▖▗▖  ▗▖▗▄▄▄▖▗▄▄▖▗▄▄▖  ▗▄▖ ▗▖ ▗▖
▐▌ ▐▌▐▛▚▖▐▌▐▌     █  ▐▌   ▐▛▚▖▐▌  █ ▐▌   ▐▌ ▐▌▐▌ ▐▌▐▌▗▞▘
▐▛▀▜▌▐▌ ▝▜▌▐▌     █  ▐▛▀▀▘▐▌ ▝▜▌  █ ▐▌▝▜▌▐▛▀▚▖▐▌ ▐▌▐▛▚▖ 
▐▌ ▐▌▐▌  ▐▌▝▚▄▄▖▗▄█▄▖▐▙▄▄▖▐▌  ▐▌  █ ▝▚▄▞▘▐▌ ▐▌▝▚▄▞▘▐▌ ▐▌

Ancient World Knowledge Agent
Powered by Grok AI • 17 Agentic Tools • Research & Visualization

Initializing AncientGrok...
✓ AncientGrok ready

You:
```

### Test Basic Functionality

Try these test queries:

**1. Simple Question:**
```
You: Who was Hammurabi?
```

Expected: Detailed historical response

**2. Database Query:**
```
You: Search CDLI for Ur III tablets
```

Expected: Tool call visible, tablet results returned

**3. Image Generation:**
```
You: Generate an image of ancient Babylon
```

Expected: Image created, auto-opens in viewer

**4. Exit:**
```
You: exit
```

Expected: "Farewell from the ancient world!" and clean shutdown

---

## Verification

### Check All Tools Work

```
You: tools
```

Should display all 17 tools across categories.

### Verify Artifacts Generated

After generating content, check:

**Images:**
```bash
ls -lh /tmp/ancientgrok_images/
```

**Reports:**
```bash
ls -lh desktop/reports/
```

**Downloaded Papers:**
```bash
ls -lh desktop/papers/
```

**CDLI Tablets:**
```bash
ls -lh /tmp/cdli_images/
```

---

## Troubleshooting

### "XAI_API_KEY not set"

**Problem:** Environment variable not configured  
**Solution:** 
```bash
export XAI_API_KEY="your-key"
```

### "ModuleNotFoundError: No module named 'xai_sdk'"

**Problem:** Dependencies not installed  
**Solution:**
```bash
cd ancientgrok
pip install -e .
```

### "pdflatex: command not found"

**Problem:** LaTeX not installed  
**Solution:** Install texlive (see Prerequisites section)

### "Failed to download paper (HTTP 403)"

**Problem:** PDF behind paywall or requires authentication  
**Solution:** Use papers from open-access sources (arXiv, institutional repos)

### CDLI API Errors (500)

**Problem:** Upstream CDLI API issues  
**Solution:** This is a known CDLI server issue, not an AncientGrok bug. Try:
- Different tablets or queries
- Use search instead of individual retrieval
- Agent provides fallback responses from training

---

## Updating

### Update AncientGrok

```bash
cd ancientgrok
git pull  # If using git
pip install -e . --upgrade
```

### Update Dependencies

```bash
pip install -r requirements.txt --upgrade
```

---

## Uninstall

```bash
pip uninstall ancientgrok
pip uninstall cdli-cli
```

Remove generated files:
```bash
rm -rf /tmp/ancientgrok_images/
rm -rf /tmp/cdli_images/
rm -rf desktop/reports/
rm -rf desktop/papers/
```

---

## Getting Help

### In-App Help

```
You: help
```

Shows commands and example queries.

### Documentation

- [README.md](README.md) - Overview and quick start
- [FEATURES.md](FEATURES.md) - Complete feature catalog
- [TESTING.md](TESTING.md) - Test documentation
- [FUTURE_TOOLS.md](FUTURE_TOOLS.md) - Roadmap

### Issues

If you encounter problems:
1. Check this SETUP guide
2. Review [TESTING.md](TESTING.md) for known issues
3. Verify API key is set correctly
4. Ensure all dependencies installed

---

## Advanced Configuration

### Use Different Grok Model

Default: `grok-4-1-fast-non-reasoning` (fast, 2-3s responses)

Alternative: `grok-4-1-fast-reasoning` (deeper analysis, 30-50s)

Edit `src/ancientgrok/cli.py` or pass model parameter to agent.

### Custom Output Directories

Edit paths in:
- `image_tools.py` - Change `/tmp/ancientgrok_images/`
- `report_tools.py` - Change `desktop/reports/`
- `bibliography_tools.py` - Change `desktop/papers/`

### Disable Auto-Open

Comment out subprocess calls in:
- `image_tools.py`
- `report_tools.py`
- `bibliography_tools.py`

---

## Next Steps

After setup, try:

1. **Explore CDLI**: `Search CDLI for your period of interest`
2. **Generate Visuals**: `Create an image of the Ishtar Gate`
3. **Download Papers**: `Find and download papers on [topic]`
4. **Create Report**: `Generate a report on Sumerian civilization`
5. **Analyze Tablets**: `Download and analyze tablet P000001`

---

**Setup Complete!** Enjoy exploring the ancient world with AncientGrok.