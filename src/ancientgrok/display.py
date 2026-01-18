"""Rich terminal UI components for AncientGrok."""

from typing import Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.markup import escape


console = Console()


STARTUP_ASCII = """
 ▗▄▖ ▗▖  ▗▖ ▗▄▄▖▗▄▄▄▖▗▄▄▄▖▗▖  ▗▖▗▄▄▄▖▗▄▄▖▗▄▄▖  ▗▄▖ ▗▖ ▗▖
▐▌ ▐▌▐▛▚▖▐▌▐▌     █  ▐▌   ▐▛▚▖▐▌  █ ▐▌   ▐▌ ▐▌▐▌ ▐▌▐▌▗▞▘
▐▛▀▜▌▐▌ ▝▜▌▐▌     █  ▐▛▀▀▘▐▌ ▝▜▌  █ ▐▌▝▜▌▐▛▀▚▖▐▌ ▐▌▐▛▚▖ 
▐▌ ▐▌▐▌  ▐▌▝▚▄▄▖▗▄█▄▖▐▙▄▄▖▐▌  ▐▌  █ ▝▚▄▞▘▐▌ ▐▌▝▚▄▞▘▐▌ ▐▌

@grok was this real?
Powered by GrokAI.
"""


def show_startup():
    """Display the startup screen."""
    console.clear()
    
    # Create startup panel with bright yellow text
    startup_text = Text(STARTUP_ASCII, style="bold bright_yellow")
    startup_panel = Panel(
        Align.center(startup_text),
        border_style="bright_yellow",  # Bright blue border
        padding=(1, 2)
    )
    
    console.print()
    console.print(startup_panel)
    console.print()
    console.print(Align.center(
        Text("Type 'help' for commands • 'tools' for capabilities • 'exit' to quit", style="dim white")
    ))
    console.print()
    console.print(Rule(style="dim bright_yellow"))
    console.print()


def show_user_message(message: str):
    """Display user message."""
    console.print()
    panel = Panel(
        message,
        title="[bold bright_yellow]You[/bold bright_yellow]",
        border_style="bright_yellow",
        padding=(0, 1)
    )
    console.print(panel)


def show_agent_thinking():
    """Show agent is thinking."""
    console.print("[dim italic bright_yellow]AncientGrok is thinking...[/dim italic bright_yellow]")


def show_tool_call(tool_name: str, arguments: str):
    """Display a tool call with formatted arguments table."""
    # Parse arguments if it's JSON
    try:
        import json
        args_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
        
        # Create a table for arguments
        if isinstance(args_dict, dict):
            if not args_dict:
                # Empty dict - show clean message
                content_text = Text("(No parameters)", style="dim white italic")
            else:
                # Create table for non-empty dict
                from rich.table import Table
                
                args_table = Table(show_header=True, header_style="bold bright_white", box=None, padding=(0, 1))
                args_table.add_column("Parameter", style="bright_white")
                args_table.add_column("Value", style="dim white")
                
                for key, value in args_dict.items():
                    # Truncate long values and escape to prevent markup interpretation
                    value_str = str(value)
                    if len(value_str) > 80:
                        value_str = value_str[:77] + "..."
                    args_table.add_row(escape(key), escape(value_str))
                
                content_text = args_table
        else:
            # Fallback for non-dict arguments
            content_text = Text(str(arguments)[:200], style="dim white")
        
        tool_panel = Panel(
            content_text,
            title=f"[bold bright_yellow]🔧 {tool_name}[/bold bright_yellow]",
            border_style="bright_yellow",
            padding=(0, 1)
        )
    except:
        # Error case - show raw
        tool_panel = Panel(
            Text(str(arguments)[:200], style="dim white"),
            title=f"[bold bright_yellow]🔧 {tool_name}[/bold bright_yellow]",
            border_style="bright_yellow",
            padding=(0, 1)
        )
    
    console.print(tool_panel)


def show_tool_result(tool_name: str, result: dict):
    """Display tool execution result."""
    import json
    
    # Format result for display
    if isinstance(result, dict):
        if "error" in result:
            # Error result
            content_text = Text(f"Error: {result['error']}", style="red")
        else:
            # Success result - show summary
            result_str = json.dumps(result, indent=2, default=str)
            # Truncate if too long
            if len(result_str) > 500:
                result_str = result_str[:500] + "\n... (truncated)"
            content_text = Text(result_str, style="dim white")
    else:
        content_text = Text(str(result)[:500], style="dim white")
    
    result_panel = Panel(
        content_text,
        title=f"[bold green]✓ {tool_name} result[/bold green]",
        border_style="green",
        padding=(0, 1)
    )
    console.print(result_panel)


def show_agent_response(content: str, tool_usage: Optional[Dict[str, int]] = None):
    """Display agent response with optional tool usage stats."""
    # Render markdown content
    md = Markdown(content)
    
    # Add tool usage footer if tools were used
    footer = ""
    if tool_usage:
        tool_list = [f"{tool}: {count}x" for tool, count in tool_usage.items()]
        footer = f"\n[dim bright_yellow]Tools used: {', '.join(tool_list)}[/dim bright_yellow]"
    
    response_panel = Panel(
        md,
        title="[bold bright_yellow]AncientGrok[/bold bright_yellow]",
        subtitle=footer if footer else None,
        border_style="bright_yellow",
        padding=(0, 1)
    )
    console.print(response_panel)
    console.print()
    console.print(Rule(style="dim bright_yellow"))
    console.print()


def show_error(error_message: str):
    """Display an error."""
    # Escape the message to prevent Rich markup interpretation (e.g., paths like [/tmp/...])
    error_panel = Panel(
        Text(error_message, style="red"),
        title="[bold red]⚠ Error[/bold red]",
        border_style="red",
        padding=(0, 1)
    )
    console.print(error_panel)
    console.print()


def show_help():
    """Display help message."""
    help_text = """
**Available Commands:**

- `help` - Show this help message
- `clear` - Clear the screen
- `tools` - Show available agentic tools
- `exit` or `quit` - Exit AncientGrok

**Example Questions:**

- "What was the significance of Uruk in ancient Mesopotamia?"
- "Explain the development of cuneiform writing"
- "Who was Gilgamesh?"
- "Compare Sumerian and Akkadian languages"
- "Search CDLI for Ur III tablets from Girsu"
- "List historical periods in the CDLI database"

**Agentic Capabilities:**

AncientGrok can autonomously:
- Search the web for scholarly resources
- Execute Python code for analysis
- Search X/Twitter for recent discussions
- Access CDLI database (500K+ cuneiform tablets)
"""
    
    console.print(Panel(
        Markdown(help_text),
        title="[bold bright_yellow]AncientGrok Help[/bold bright_yellow]",
        border_style="bright_yellow"
    ))


def show_tools_info():
    """Display information about available tools."""
    tools_text = """
**Server-Side Agentic Tools (3):**

- 🌐 **web_search** - Autonomous internet research
  - Finds scholarly articles, recent discoveries, historical context
  - Cost: $5 per 1,000 calls

- 🐦 **x_search** - Social media and academic discussions  
  - Recent scholarly discussions, conference announcements
  - Cost: $5 per 1,000 calls

- 💻 **code_execution** - Python computational analysis
  - Data analysis, calculations, text processing
  - Cost: $5 per 1,000 calls

**Client-Side CDLI Tools (5) - 500K+ Cuneiform Tablets:**

- 🔍 **search_cdli** - Search tablets by period, provenance, genre, keyword
  - Returns tablet metadata (museum numbers, dates, locations)

- 📜 **get_tablet_details** - Full metadata for specific P-numbers
  - Dimensions, language, genre, inscription availability
  - Museum location and catalog numbers

- 🖼️ **download_tablet_image** - High-resolution photos and linearts
  - Saved to /tmp/cdli_images/
  - Verified: 7.7MB downloaded across 5 tablets

- 📅 **list_periods** - All historical periods (32 total)
  - From Uruk III/IV (3350 BCE) to Neo-Babylonian (539 BCE)

- 🏛️ **list_collections** - Museums holding artifacts (100+)
  - British Museum, Louvre, Yale, Penn, Berlin, Iraq Museum, etc.

**Client-Side Open Context Tools (3) - Archaeological Database:**

- 🏺 **search_open_context** - Search excavation records
  - Animal bones, ceramics, architecture, burials
  - Verified: 147,958 Çatalhöyük records, 879 Troy, 45 Göbekli Tepe, 16 Hattusa

- 📊 **get_opencontext_attributes** - Discover available data fields
  - Standardized measurements (Von Den Driesch)
  - Taxonomic classifications
  - Project-specific attributes

- 🔬 **get_detailed_opencontext_records** - Comprehensive artifact data
  - Full measurements and dimensions
  - Classifications and taxonomic IDs
  - Manufacturing and use-wear analysis
  - Verified: ~200 detailed bone tool records retrieved

**Client-Side Cuneiform Reference (2) - 1,205 Unicode Signs:**

- 📖 **lookup_cuneiform_sign** - Query signs by name, character, or code
  - Loads complete 1,205-line database
  - Returns sign data for parsing
  - Verified: Database loads successfully (63KB file)

- 📚 **list_cuneiform_signs** - Browse and filter signs
  - Filter by name pattern (e.g., "KING", "WATER", "A")
  - Pagination support
  - Returns parsed sign list with Unicode characters

**Client-Side Vision Tools (1):**

- 👁️ **view_analyze_image** - Analyze images with Grok's vision
  - Examine CDLI tablet photos
  - Analyze generated images
  - View archaeological artifacts
  - Verified: Successfully analyzed P120999 tablet photo

**Client-Side Paper Tools (1):**

- 📥 **download_paper** - Download academic PDFs
  - Works with arXiv, JSTOR, institutional repositories
  - Auto-opens in PDF viewer
  - Saves to desktop/papers/
  - Verified: 1.1MB Akkadian NMT paper downloaded successfully

**Client-Side Creative Tools (2):**

- 🎨 **generate_image** - Grok Imagine visualizations
  - Historical reconstructions, maps, diagrams
  - Auto-opens in image viewer
  - Saves to /tmp/ancientgrok_images/
  - Verified: 9 images generated (4MB total)

- 📝 **create_research_report** - LaTeX research papers
  - Compiles to PDF with pdflatex
  - Auto-opens in PDF viewer
  - Saves to desktop/reports/
  - Verified: 3 PDFs compiled (1.1MB total, including 902KB scholarly study)

**Client-Side Media Tools (1):**

- ✏️ **edit_image** - Modify images
  - Add details, enhance, restore
  - Works with generated or downloaded images

**How It Works:**

When you ask a question, AncientGrok autonomously decides which tools to use:
1. Answer from training knowledge when appropriate
2. Search databases (CDLI, Open Context) for primary sources
3. Look up cuneiform signs when needed
4. Download papers for detailed reference
5. Generate images to visualize concepts
6. Execute code for calculations
7. Create reports to synthesize research
8. Use vision to analyze images

Tool calls display in real-time with:
- Rich tables showing parameters
- Per-turn cost tracking
- Session cost summaries
- Clean visual formatting
"""
    
    console.print(Panel(
        Markdown(tools_text),
        title="[bold bright_yellow]18 Agentic Research Tools[/bold bright_yellow]",
        border_style="bright_yellow"
    ))