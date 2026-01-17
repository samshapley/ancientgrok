"""Display utilities for formatting CDLI data."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()


def format_tablet_summary(tablet: dict[str, Any]) -> str:
    """Format a tablet for brief display."""
    parts = []
    
    if "designation" in tablet:
        parts.append(tablet["designation"])
    
    if "museum_no" in tablet:
        parts.append(f"[dim](Museum: {tablet['museum_no']})[/dim]")
    
    if "period" in tablet:
        if isinstance(tablet["period"], dict):
            parts.append(f"[cyan]{tablet['period'].get('period', 'N/A')}[/cyan]")
        else:
            parts.append(f"[cyan]{tablet['period']}[/cyan]")
    
    return " | ".join(parts) if parts else str(tablet.get("id", "Unknown"))


def display_search_results(results: list[dict[str, Any]], total: int, page: int) -> None:
    """Display search results in a formatted table."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    console.print(f"\n[bold]Found {total} results[/bold] (Showing page {page})\n")

    # Create a table with key fields
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Designation")
    table.add_column("Museum No")
    table.add_column("Period")
    table.add_column("Excavation No", overflow="fold")

    for tablet in results[:25]:  # Limit display
        period_str = "N/A"
        if "period" in tablet:
            if isinstance(tablet["period"], dict):
                period_str = tablet["period"].get("period", "N/A")
            else:
                period_str = str(tablet["period"])

        table.add_row(
            str(tablet.get("id", "")),
            str(tablet.get("designation", "N/A"))[:50],
            str(tablet.get("museum_no", "N/A"))[:30],
            period_str[:40],
            str(tablet.get("excavation_no", "N/A"))[:30],
        )

    console.print(table)
    
    if len(results) > 25:
        console.print(f"\n[dim]... and {len(results) - 25} more results[/dim]")


def display_tablet_detail(tablet: dict[str, Any]) -> None:
    """Display detailed tablet information."""
    console.print("\n[bold cyan]Tablet Details[/bold cyan]\n")

    # Basic info
    info_tree = Tree("[bold]Basic Information[/bold]")
    info_tree.add(f"ID: {tablet.get('id', 'N/A')}")
    info_tree.add(f"Designation: {tablet.get('designation', 'N/A')}")
    info_tree.add(f"Museum No: {tablet.get('museum_no', 'N/A')}")
    info_tree.add(f"Excavation No: {tablet.get('excavation_no', 'N/A')}")
    
    # Period
    if "period" in tablet:
        period = tablet["period"]
        if isinstance(period, dict):
            info_tree.add(f"Period: {period.get('period', 'N/A')}")
        else:
            info_tree.add(f"Period: {period}")

    console.print(info_tree)

    # Physical attributes
    if any(k in tablet for k in ["height", "width", "thickness"]):
        phys_tree = Tree("\n[bold]Physical Attributes[/bold]")
        if "height" in tablet:
            phys_tree.add(f"Height: {tablet['height']} mm")
        if "width" in tablet:
            phys_tree.add(f"Width: {tablet['width']} mm")
        if "thickness" in tablet:
            phys_tree.add(f"Thickness: {tablet['thickness']} mm")
        console.print(phys_tree)

    # Inscription
    if "inscription" in tablet and tablet["inscription"]:
        insc = tablet["inscription"]
        console.print(f"\n[bold]Inscription[/bold]")
        console.print(f"ID: {insc.get('id', 'N/A')}")
        if "atf" in insc:
            atf_preview = insc["atf"][:200]
            console.print(f"ATF (preview): [dim]{atf_preview}...[/dim]")

    # Publications
    if "publications" in tablet and tablet["publications"]:
        pubs = tablet["publications"]
        pub_tree = Tree(f"\n[bold]Publications ({len(pubs)})[/bold]")
        for pub_link in pubs[:3]:
            if "publication" in pub_link:
                pub = pub_link["publication"]
                pub_str = f"{pub.get('designation', 'N/A')} ({pub.get('year', 'N/A')})"
                pub_tree.add(pub_str)
        console.print(pub_tree)


def display_entity_list(entities: list[dict[str, Any]], entity_type: str) -> None:
    """Display a list of entities."""
    if not entities:
        console.print("[yellow]No entities found.[/yellow]")
        return

    console.print(f"\n[bold]{entity_type.title()}[/bold]\n")

    # Try to find common fields
    if entities:
        first = entities[0]
        
        # For simple entities (just id and name)
        if len(first.keys()) <= 3:
            for entity in entities[:30]:
                # Try different name fields
                name = (
                    entity.get("name")
                    or entity.get(entity_type.lower())
                    or entity.get("period")
                    or entity.get("genre")
                    or entity.get("language")
                    or str(entity)
                )
                console.print(f"  • {name}")
        else:
            # For complex entities, use a table
            table = Table()
            keys = list(first.keys())[:5]  # First 5 fields
            for key in keys:
                table.add_column(key.replace("_", " ").title())
            
            for entity in entities[:20]:
                row = []
                for key in keys:
                    value = entity.get(key, "")
                    if isinstance(value, dict):
                        value = value.get("name", value.get("period", str(value)))
                    row.append(str(value)[:40])
                table.add_row(*row)
            
            console.print(table)


def display_json_pretty(data: Any) -> None:
    """Display JSON with syntax highlighting."""
    from rich.syntax import Syntax
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(syntax)