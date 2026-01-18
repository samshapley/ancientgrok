"""Interactive CLI application for AncientGrok."""

import os
import sys
from typing import Optional

from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel

from .agent import AncientGrokAgent
from .display import (
    show_startup,
    show_user_message,
    show_agent_thinking,
    show_tool_call,
    show_tool_result,
    show_agent_response,
    show_error,
    show_help,
    show_tools_info,
    console,
)


def run_chat_loop(agent: AncientGrokAgent):
    """Run the interactive chat loop.
    
    Args:
        agent: AncientGrok agent instance
    """
    console.print("[dim]Chat started. Type 'exit' to quit.[/dim]\n")
    
    # Session cost tracking
    session_tokens = {"input": 0, "output": 0, "total_cost": 0.0}
    
    # Grok pricing (grok-4-1-fast-non-reasoning)
    input_cost_per_1m = 0.20
    output_cost_per_1m = 0.50
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("[bold bright_yellow]You[/bold bright_yellow]")
            
            # Check for commands
            if user_input.lower() in ('exit', 'quit'):
                # Display final session cost
                if session_tokens["total_cost"] > 0:
                    console.print()
                    console.print(Panel(
                        f"[bright_white]Session Summary[/bright_white]\n\n"
                        f"Input tokens:  {session_tokens['input']:,}\n"
                        f"Output tokens: {session_tokens['output']:,}\n"
                        f"Total cost:    [bright_yellow]${session_tokens['total_cost']:.4f}[/bright_yellow]",
                        title="[bold bright_yellow]💰 Cost Summary[/bold bright_yellow]",
                        border_style="bright_yellow"
                    ))
                console.print("\n[bright_yellow]Farewell from the ancient world![/bright_yellow]\n")
                break
            
            if user_input.lower() == 'help':
                show_help()
                continue
            
            if user_input.lower() == 'clear':
                console.clear()
                continue
            
            if user_input.lower() == 'tools':
                show_tools_info()
                continue
            
            if not user_input.strip():
                continue
            
            # Display user message
            show_user_message(user_input)
            
            # Show thinking indicator
            show_agent_thinking()
            
            # Get streaming response
            try:
                accumulated_text = []
                tool_usage = {}
                streaming_started = False
                turn_tokens = {"input": 0, "output": 0}
                
                for event in agent.send_message(user_input):
                    event_type = event.get("type")
                    
                    if event_type == "tool_call":
                        # Show tool call
                        tool_name = event.get("tool", "unknown")
                        tool_args = event.get("arguments", {})
                        show_tool_call(tool_name, tool_args)
                        
                        # Track tool usage
                        tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
                    
                    elif event_type == "tool_result":
                        # Show tool result (client-side tools only)
                        tool_name = event.get("tool", "unknown")
                        result = event.get("result", {})
                        show_tool_result(tool_name, result)
                    
                    elif event_type == "text":
                        # Stream text chunks live as they arrive
                        chunk = event.get("content", "")
                        if chunk:
                            if not streaming_started:
                                streaming_started = True
                            
                            # Print chunk immediately without newline
                            console.print(chunk, end="", highlight=False)
                            accumulated_text.append(chunk)
                    
                    elif event_type == "usage":
                        # Track token usage from this turn
                        usage = event.get("usage", {})
                        turn_tokens["input"] = usage.get("input_tokens", 0)
                        turn_tokens["output"] = usage.get("output_tokens", 0)
                    
                    elif event_type == "complete":
                        # Streaming complete - add final formatting
                        if streaming_started:
                            console.print()  # Add newline after streaming text
                        
                        # Calculate and display turn cost BEFORE tools/divider
                        turn_cost = (
                            (turn_tokens["input"] / 1_000_000) * input_cost_per_1m +
                            (turn_tokens["output"] / 1_000_000) * output_cost_per_1m
                        )
                        session_tokens["input"] += turn_tokens["input"]
                        session_tokens["output"] += turn_tokens["output"]
                        session_tokens["total_cost"] += turn_cost
                        
                        # Show tool usage and cost together
                        final_text = "".join(accumulated_text)
                        if final_text.strip() or tool_usage:
                            # Build footer with tools and cost
                            footer_parts = []
                            if tool_usage:
                                tool_list = [f"{tool}: {count}x" for tool, count in tool_usage.items()]
                                footer_parts.append(f"[dim bright_yellow]Tools: {', '.join(tool_list)}[/dim bright_yellow]")
                            
                            if turn_cost > 0:
                                footer_parts.append(
                                    f"[dim bright_yellow]Cost: ${turn_cost:.4f} | "
                                    f"Session: ${session_tokens['total_cost']:.4f}[/dim bright_yellow]"
                                )
                            
                            # Display footer
                            if footer_parts:
                                console.print()
                                for part in footer_parts:
                                    console.print(part)
                            
                            # Now add divider for next turn
                            console.print()
                            from rich.rule import Rule
                            console.print(Rule(style="dim bright_yellow"))
                            console.print()
                        else:
                            # If no text was generated but tools were used,
                            # show acknowledgment
                            if tool_usage:
                                show_agent_response(
                                    "Tool execution completed.",
                                    tool_usage
                                )
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Response interrupted[/yellow]\n")
                continue
            except Exception as e:
                show_error(f"Error: {str(e)}")
        
        except KeyboardInterrupt:
            console.print("\n[bright_yellow]Exiting...[/bright_yellow]\n")
            break
        except EOFError:
            console.print("\n[bright_yellow]Exiting...[/bright_yellow]\n")
            break


def main():
    """Main entry point for AncientGrok CLI."""
    # Check for API key
    if not os.getenv("XAI_API_KEY"):
        console.print("[red]Error: XAI_API_KEY environment variable not set[/red]")
        console.print("[yellow]Set it with: export XAI_API_KEY='your-key-here'[/yellow]")
        sys.exit(1)
    
    # Show startup screen
    show_startup()
    
    try:
        # Initialize agent
        console.print("[dim]Initializing AncientGrok...[/dim]")
        agent = AncientGrokAgent()
        console.print("[green]✓ AncientGrok ready[/green]\n")
        
        # Run chat loop
        run_chat_loop(agent)
        
    except Exception as e:
        show_error(f"Failed to initialize: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()