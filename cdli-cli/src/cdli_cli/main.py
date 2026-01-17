"""CDLI CLI - Main application entry point."""

import json
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from . import __version__
from .client import CDLIClient
from .display import display_entity_list, display_search_results, display_tablet_detail
from .models import (
    APIError,
    BibliographyFormat,
    EntityType,
    FORMAT_EXTENSIONS,
    InscriptionFormat,
    NotFoundError,
    OutputFormat,
    TabularFormat,
)

# Create the main app
app = typer.Typer(
    name="cdli",
    help="Command-line interface for the Cuneiform Digital Library Initiative (CDLI) API.",
    add_completion=True,
    no_args_is_help=True,
)

# Create sub-apps for command groups
get_app = typer.Typer(help="Get individual entities by ID.")
list_app = typer.Typer(help="List entities.")
export_app = typer.Typer(help="Export data in tabular formats.")
search_app = typer.Typer(help="Search the CDLI database.")
bib_app = typer.Typer(help="Get bibliographies.")
image_app = typer.Typer(help="Download tablet images.")

app.add_typer(get_app, name="get")
app.add_typer(list_app, name="list")
app.add_typer(export_app, name="export")
app.add_typer(search_app, name="search")
app.add_typer(bib_app, name="bib")
app.add_typer(image_app, name="image")

console = Console()

# Common options
BaseUrlOption = Annotated[
    Optional[str],
    typer.Option("--base-url", "-b", help="Override CDLI base URL"),
]
OutputOption = Annotated[
    Optional[Path],
    typer.Option("--output", "-o", help="Output file path (default: stdout)"),
]
FormatOption = Annotated[
    OutputFormat,
    typer.Option("--format", "-f", help="Output format"),
]
PageOption = Annotated[
    int,
    typer.Option("--page", "-p", help="Page number"),
]
PerPageOption = Annotated[
    int,
    typer.Option("--per-page", "-n", help="Results per page"),
]


def handle_error(e: Exception) -> None:
    """Handle and display errors."""
    if isinstance(e, NotFoundError):
        console.print(f"[red]Not found:[/red] {e}")
    elif isinstance(e, APIError):
        console.print(f"[red]API Error ({e.status_code}):[/red] {e.message}")
    else:
        console.print(f"[red]Error:[/red] {e}")
    raise typer.Exit(1)


def output_result(
    client: CDLIClient,
    content: any,
    output: Optional[Path],
    format_name: str,
) -> None:
    """Output result to file or stdout."""
    client.save_output(content, output, format_name)
    if output:
        console.print(f"[green]Saved to:[/green] {output}")


# =============================================================================
# Version Command
# =============================================================================


@app.command()
def version() -> None:
    """Show version information."""
    rprint(f"cdli-cli version {__version__}")


# =============================================================================
# Get Commands
# =============================================================================


@get_app.command("tablet")
def get_tablet(
    tablet_id: Annotated[str, typer.Argument(help="Tablet ID (e.g., P000001)")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get a tablet by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_tablet(tablet_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("artifact")
def get_artifact(
    artifact_id: Annotated[str, typer.Argument(help="Artifact ID")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get an artifact by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_artifact(artifact_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("publication")
def get_publication(
    publication_id: Annotated[str, typer.Argument(help="Publication ID")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get a publication by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_publication(publication_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("inscription")
def get_inscription(
    tablet_id: Annotated[str, typer.Argument(help="Tablet ID")],
    format: Annotated[
        InscriptionFormat,
        typer.Option("--format", "-f", help="Inscription format"),
    ] = InscriptionFormat.ATF,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get inscription text for a tablet."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_inscription(tablet_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("collection")
def get_collection(
    collection_id: Annotated[str, typer.Argument(help="Collection ID")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get a collection by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_collection(collection_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("period")
def get_period(
    period_id: Annotated[str, typer.Argument(help="Period ID")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get a period by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_period(period_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("provenance")
def get_provenance(
    provenance_id: Annotated[str, typer.Argument(help="Provenance ID")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get a provenance by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_provenance(provenance_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("genre")
def get_genre(
    genre_id: Annotated[str, typer.Argument(help="Genre ID")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get a genre by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_genre(genre_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("language")
def get_language(
    language_id: Annotated[str, typer.Argument(help="Language ID")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get a language by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_language(language_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("material")
def get_material(
    material_id: Annotated[str, typer.Argument(help="Material ID")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get a material by ID."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_material(material_id, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@get_app.command("ids")
def get_by_ids(
    ids: Annotated[list[str], typer.Argument(help="Artifact IDs (P, Q, or S numbers)")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get multiple artifacts by their P/Q/S numbers."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_by_ids(ids, format)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


# =============================================================================
# List Commands
# =============================================================================


def display_list_results(results: list, title: str) -> None:
    """Display list results in a table."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(title=title)
    
    # Add columns based on first result's keys
    if results:
        for key in results[0].keys():
            table.add_column(str(key).replace("_", " ").title())
        
        for item in results[:50]:  # Limit display
            table.add_row(*[str(v)[:50] for v in item.values()])

    console.print(table)


@list_app.command("tablets")
def list_tablets(
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """List tablets."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.list_tablets(page, per_page)
            if output:
                output_result(client, {"total": result.total, "results": result.results}, output, "json")
            else:
                console.print(f"[bold]Total: {result.total}[/bold] (Page {result.page})")
                display_list_results(result.results, "Tablets")
    except Exception as e:
        handle_error(e)


@list_app.command("collections")
def list_collections(
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """List collections."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.list_collections(page, per_page)
            if output:
                output_result(client, {"total": result.total, "results": result.results}, output, "json")
            else:
                console.print(f"[bold]Total: {result.total}[/bold] (Page {result.page})")
                display_list_results(result.results, "Collections")
    except Exception as e:
        handle_error(e)


@list_app.command("periods")
def list_periods(
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """List historical periods."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.list_periods(page, per_page)
            if output:
                output_result(client, {"total": result.total, "results": result.results}, output, "json")
            else:
                display_entity_list(result.results, "periods")
                console.print(f"\n[dim]Page {result.page} | Total: {result.total}[/dim]")
    except Exception as e:
        handle_error(e)


@list_app.command("genres")
def list_genres(
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """List text genres."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.list_genres(page, per_page)
            if output:
                output_result(client, {"total": result.total, "results": result.results}, output, "json")
            else:
                console.print(f"[bold]Total: {result.total}[/bold] (Page {result.page})")
                display_list_results(result.results, "Genres")
    except Exception as e:
        handle_error(e)


@list_app.command("languages")
def list_languages(
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """List languages."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.list_languages(page, per_page)
            if output:
                output_result(client, {"total": result.total, "results": result.results}, output, "json")
            else:
                console.print(f"[bold]Total: {result.total}[/bold] (Page {result.page})")
                display_list_results(result.results, "Languages")
    except Exception as e:
        handle_error(e)


@list_app.command("provenances")
def list_provenances(
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """List provenances (find locations)."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.list_provenances(page, per_page)
            if output:
                output_result(client, {"total": result.total, "results": result.results}, output, "json")
            else:
                console.print(f"[bold]Total: {result.total}[/bold] (Page {result.page})")
                display_list_results(result.results, "Provenances")
    except Exception as e:
        handle_error(e)


# =============================================================================
# Search Commands
# =============================================================================


@search_app.command("query")
def search_query(
    query: Annotated[str, typer.Argument(help="Search query")],
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """Search the CDLI database."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.search(query, page, per_page)
            if output:
                output_result(client, {"total": result.total, "results": result.results}, output, "json")
            else:
                display_search_results(result.results, result.total, result.page)
    except Exception as e:
        handle_error(e)


@search_app.command("advanced")
def search_advanced(
    designation: Annotated[Optional[str], typer.Option("--designation", "-d", help="Tablet designation")] = None,
    period: Annotated[Optional[str], typer.Option("--period", help="Historical period")] = None,
    provenance: Annotated[Optional[str], typer.Option("--provenance", help="Find location")] = None,
    genre: Annotated[Optional[str], typer.Option("--genre", help="Text genre")] = None,
    language: Annotated[Optional[str], typer.Option("--language", help="Language")] = None,
    collection: Annotated[Optional[str], typer.Option("--collection", help="Collection")] = None,
    material: Annotated[Optional[str], typer.Option("--material", help="Material")] = None,
    inscription: Annotated[Optional[str], typer.Option("--inscription", "-i", help="Inscription text")] = None,
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """Advanced search with specific field filters."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.advanced_search(
                designation=designation,
                period=period,
                provenance=provenance,
                genre=genre,
                language=language,
                collection=collection,
                material=material,
                inscription=inscription,
                page=page,
                per_page=per_page,
            )
            if output:
                output_result(client, {"total": result.total, "results": result.results}, output, "json")
            else:
                console.print(f"[bold]Found: {result.total} results[/bold] (Page {result.page})")
                display_list_results(result.results, "Advanced Search Results")
    except Exception as e:
        handle_error(e)


# =============================================================================
# Export Commands
# =============================================================================


@export_app.command("tablets")
def export_tablets(
    format: Annotated[
        TabularFormat,
        typer.Option("--format", "-f", help="Export format"),
    ] = TabularFormat.CSV,
    page: PageOption = 1,
    per_page: PerPageOption = 100,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Export tablets in tabular format."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.export_tablets(format, page, per_page)
            
            if output is None:
                ext = FORMAT_EXTENSIONS.get(format.value, ".csv")
                output = Path(f"cdli_tablets_p{page}{ext}")
            
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@export_app.command("publications")
def export_publications(
    format: Annotated[
        TabularFormat,
        typer.Option("--format", "-f", help="Export format"),
    ] = TabularFormat.CSV,
    page: PageOption = 1,
    per_page: PerPageOption = 100,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Export publications in tabular format."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.export_publications(format, page, per_page)
            
            if output is None:
                ext = FORMAT_EXTENSIONS.get(format.value, ".csv")
                output = Path(f"cdli_publications_p{page}{ext}")
            
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


# =============================================================================
# Bibliography Commands
# =============================================================================


@bib_app.command("tablet")
def bib_tablet(
    tablet_id: Annotated[str, typer.Argument(help="Tablet ID")],
    format: Annotated[
        BibliographyFormat,
        typer.Option("--format", "-f", help="Bibliography format"),
    ] = BibliographyFormat.BIBTEX,
    style: Annotated[
        Optional[str],
        typer.Option("--style", "-s", help="CSL style for formatted output"),
    ] = None,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get bibliography for a tablet."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_tablet_bibliography(tablet_id, format, style)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


@bib_app.command("publication")
def bib_publication(
    publication_id: Annotated[str, typer.Argument(help="Publication ID")],
    format: Annotated[
        BibliographyFormat,
        typer.Option("--format", "-f", help="Bibliography format"),
    ] = BibliographyFormat.BIBTEX,
    style: Annotated[
        Optional[str],
        typer.Option("--style", "-s", help="CSL style for formatted output"),
    ] = None,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Get bibliography for a publication."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result = client.get_publication_bibliography(publication_id, format, style)
            output_result(client, result, output, format.value)
    except Exception as e:
        handle_error(e)


# =============================================================================
# Direct Access Commands (shortcuts)
# =============================================================================


@app.command("tablet")
def tablet_shortcut(
    tablet_id: Annotated[str, typer.Argument(help="Tablet ID (e.g., P000001)")],
    format: FormatOption = OutputFormat.JSON,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """[Shortcut] Get a tablet by ID. Same as 'cdli get tablet'."""
    get_tablet(tablet_id, format, output, base_url)


@app.command("inscription")
def inscription_shortcut(
    tablet_id: Annotated[str, typer.Argument(help="Tablet ID")],
    format: Annotated[
        InscriptionFormat,
        typer.Option("--format", "-f", help="Inscription format"),
    ] = InscriptionFormat.ATF,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """[Shortcut] Get inscription text. Same as 'cdli get inscription'."""
    get_inscription(tablet_id, format, output, base_url)


@app.command("find")
def find_shortcut(
    query: Annotated[str, typer.Argument(help="Search query")],
    page: PageOption = 1,
    per_page: PerPageOption = 25,
    base_url: BaseUrlOption = None,
    output: OutputOption = None,
) -> None:
    """[Shortcut] Search the database. Same as 'cdli search query'."""
    search_query(query, page, per_page, base_url, output)


# =============================================================================
# Image Commands
# =============================================================================


@image_app.command("photo")
def download_photo(
    tablet_id: Annotated[str, typer.Argument(help="Tablet ID (P-number)")],
    thumbnail: Annotated[bool, typer.Option("--thumbnail", "-t", help="Download thumbnail instead of full resolution")] = False,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Download a tablet photograph."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result_path = client.download_image(
                tablet_id,
                image_type="photo",
                thumbnail=thumbnail,
                output_path=output,
            )
            console.print(f"[green]Downloaded:[/green] {result_path}")
    except Exception as e:
        handle_error(e)


@image_app.command("lineart")
def download_lineart(
    tablet_id: Annotated[str, typer.Argument(help="Tablet ID (P-number)")],
    thumbnail: Annotated[bool, typer.Option("--thumbnail", "-t", help="Download thumbnail")] = False,
    output: OutputOption = None,
    base_url: BaseUrlOption = None,
) -> None:
    """Download a tablet line art drawing."""
    try:
        with CDLIClient(base_url=base_url) as client:
            result_path = client.download_image(
                tablet_id,
                image_type="lineart",
                thumbnail=thumbnail,
                output_path=output,
            )
            console.print(f"[green]Downloaded:[/green] {result_path}")
    except Exception as e:
        handle_error(e)


@image_app.command("both")
def download_both(
    tablet_id: Annotated[str, typer.Argument(help="Tablet ID (P-number)")],
    thumbnail: Annotated[bool, typer.Option("--thumbnail", "-t", help="Download thumbnails")] = False,
    base_url: BaseUrlOption = None,
) -> None:
    """Download both photo and lineart for a tablet."""
    try:
        with CDLIClient(base_url=base_url) as client:
            photo_path = client.download_image(tablet_id, "photo", thumbnail)
            console.print(f"[green]Downloaded photo:[/green] {photo_path}")
            
            try:
                lineart_path = client.download_image(tablet_id, "lineart", thumbnail)
                console.print(f"[green]Downloaded lineart:[/green] {lineart_path}")
            except NotFoundError:
                console.print("[yellow]Note:[/yellow] Lineart not available for this tablet")
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    app()