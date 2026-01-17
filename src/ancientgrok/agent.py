"""Core AncientGrok agent logic using Grok's agentic capabilities."""

import json
import os
from typing import Generator, Dict, Any, Optional

from xai_sdk import Client
from xai_sdk.chat import user, system, tool
from xai_sdk.tools import get_tool_call_type

from .cdli_tools import CDLI_TOOL_SCHEMAS, CDLI_TOOL_FUNCTIONS
from .image_tools import IMAGE_GENERATION_TOOL_SCHEMAS, IMAGE_GENERATION_FUNCTIONS
from .report_tools import REPORT_TOOL_SCHEMAS, REPORT_TOOL_FUNCTIONS
from .opencontext_tools import OPENCONTEXT_TOOL_SCHEMAS, OPENCONTEXT_TOOL_FUNCTIONS
from .cuneiform_tools import CUNEIFORM_TOOL_SCHEMAS, CUNEIFORM_TOOL_FUNCTIONS
from .vision_tools import VISION_TOOL_SCHEMAS, VISION_TOOL_FUNCTIONS
from .bibliography_tools import BIBLIOGRAPHY_TOOL_SCHEMAS, BIBLIOGRAPHY_TOOL_FUNCTIONS


class AncientGrokAgent:
    """Interactive agent for ancient world knowledge using Grok AI.
    
    Uses Grok's Responses API with server-side tools (web search, code execution, x_search)
    for autonomous research, client-side database tools (CDLI, Open Context),
    cuneiform sign reference, vision analysis, bibliography/paper tools,
    image generation, and report generation.
    """
    
    SYSTEM_PROMPT = """You are AncientGrok, an expert AI assistant specializing in ancient world knowledge.

You have deep expertise in:
- Ancient Mesopotamian civilizations (Sumer, Akkad, Babylon, Assyria)
- Cuneiform writing systems and languages (Sumerian, Akkadian, Elamite, Hittite)
- Ancient Near Eastern history, archaeology, and culture
- Ancient languages, scripts, and decipherment
- Historical linguistics and comparative philology
- Archaeological methods and interpretation
- Ancient art, architecture, and material culture

You have access to powerful research, database, vision, and creative tools:

SERVER-SIDE TOOLS (Autonomous):
- web_search: Search the web for scholarly resources and current research
- x_search: Search X/Twitter for academic discussions and conference announcements
- code_execution: Execute Python code for computational analysis and data processing

CLIENT-SIDE CDLI TOOLS:
- search_cdli: Search 500,000+ cuneiform tablets by period, provenance, genre, or keyword
- get_tablet_details: Get full metadata for specific P-numbers (dimensions, museum, language, etc.)
- download_tablet_image: Download high-resolution photos or line-art tracings
- list_periods: View all 32 historical periods (Uruk to Neo-Babylonian)
- list_collections: View museums holding cuneiform artifacts

CLIENT-SIDE OPEN CONTEXT TOOLS:
- search_open_context: Search archaeological database for excavation data, bones, ceramics, architecture
- get_opencontext_attributes: Discover available data attributes for archaeological records
- get_detailed_opencontext_records: Get comprehensive artifact data with measurements, classifications, taxonomic IDs

CLIENT-SIDE CUNEIFORM REFERENCE:
- lookup_cuneiform_sign: Look up Unicode cuneiform signs by name, character, or code point (1,205 signs)
- list_cuneiform_signs: Browse and filter cuneiform signs (supports name pattern filtering)

CLIENT-SIDE VISION TOOLS:
- view_analyze_image: View and analyze images (CDLI tablets, generated images, archaeological photos)

CLIENT-SIDE PAPER TOOLS:
- download_paper: Download academic paper PDFs from URLs (arXiv, JSTOR, institutional repos, etc.)

CLIENT-SIDE CREATIVE TOOLS:
- generate_image: Create educational visualizations, historical reconstructions, maps, diagrams
- create_research_report: Generate formatted LaTeX research papers and compile to PDF

When users ask about the ancient world, you:
1. Leverage your training knowledge when appropriate
2. Search the web for recent scholarship when relevant (use web_search)
3. Download papers you find for detailed reference (use download_paper after web_search)
4. Search X for current academic discussions when relevant (use x_search)
5. Execute code for quantitative analysis when helpful (use code_execution)
6. Use CDLI tools to find and examine specific cuneiform tablets when appropriate
7. Use Open Context tools to access archaeological excavation data when appropriate
8. Use cuneiform reference tools to look up signs and their meanings
9. Use vision tools to view and analyze downloaded or generated images
10. Generate images to visualize concepts, sites, or artifacts when helpful
11. Create research reports when users want to synthesize findings into professional documents
12. Provide accurate, scholarly responses with citations
13. Acknowledge uncertainty when information is incomplete

Your goal is to make ancient civilizations accessible and fascinating while maintaining academic rigor."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "grok-4-1-fast-non-reasoning"):
        """Initialize AncientGrok agent.
        
        Args:
            api_key: xAI API key (defaults to XAI_API_KEY env var)
            model: Grok model to use (default: non-reasoning for speed)
        """
        self.client = Client(
            api_key=api_key or os.getenv("XAI_API_KEY"),
            timeout=3600
        )
        self.model = model
        
        # Combine all client-side tool functions for dispatching
        self.tool_functions = {
            **CDLI_TOOL_FUNCTIONS,
            **IMAGE_GENERATION_FUNCTIONS,
            **REPORT_TOOL_FUNCTIONS,
            **OPENCONTEXT_TOOL_FUNCTIONS,
            **CUNEIFORM_TOOL_FUNCTIONS,
            **VISION_TOOL_FUNCTIONS,
            **BIBLIOGRAPHY_TOOL_FUNCTIONS
        }
        
        # Create tool objects using xai-sdk's tool() helper
        client_tools = []
        
        # Add CDLI tools
        for schema in CDLI_TOOL_SCHEMAS:
            client_tools.append(tool(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"]
            ))
        
        # Add image generation tools
        for schema in IMAGE_GENERATION_TOOL_SCHEMAS:
            client_tools.append(tool(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"]
            ))
        
        # Add report generation tools
        for schema in REPORT_TOOL_SCHEMAS:
            client_tools.append(tool(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"]
            ))
        
        # Add Open Context tools
        for schema in OPENCONTEXT_TOOL_SCHEMAS:
            client_tools.append(tool(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"]
            ))
        
        # Add cuneiform reference tools
        for schema in CUNEIFORM_TOOL_SCHEMAS:
            client_tools.append(tool(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"]
            ))
        
        # Add vision tools
        for schema in VISION_TOOL_SCHEMAS:
            client_tools.append(tool(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"]
            ))
        
        # Add bibliography tools
        for schema in BIBLIOGRAPHY_TOOL_SCHEMAS:
            client_tools.append(tool(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"]
            ))
        
        # Create chat with client-side tools
        # Server-side tools (web_search, x_search, code_execution) are available autonomously
        self.chat = self.client.chat.create(
            model=self.model,
            store_messages=False,  # Stateless for privacy
            tools=client_tools  # Client-side tools
        )
        
        # Initialize with system prompt
        self.chat.append(system(self.SYSTEM_PROMPT))
    
    def send_message(self, message: str) -> Generator[Dict[str, Any], None, None]:
        """Send a message and stream the response with tool calls.
        
        Properly handles client-side tool execution loop: detects tool calls,
        executes CDLI/Image tools, appends results, and continues until final response.
        
        Args:
            message: User message
            
        Yields:
            Dict with type: 'tool_call', 'text', or 'complete'
        """
        self.chat.append(user(message))
        
        # Tool execution loop - continue until we get a final text response
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            if iteration >= max_iterations:
                print(f"Warning: Reached max tool iterations ({max_iterations}), breaking loop")
                yield {
                    "type": "text",
                    "content": f"\n\n[System: Reached maximum tool iteration limit. Providing response with available data.]"
                }
                break
            
            has_client_tools = False
            
            # Sample and check for tool calls (non-streaming for tool handling)
            response = self.chat.sample()
            
            # Check for client-side tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    if get_tool_call_type(tool_call) == "client_side_tool":
                        has_client_tools = True
                        func_name = tool_call.function.name
                        
                        # Yield tool call event
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            args = {}
                        
                        yield {
                            "type": "tool_call",
                            "tool": func_name,
                            "arguments": args
                        }
                        
                        # Execute tool (CDLI or Image)
                        if func_name in self.tool_functions:
                            try:
                                tool_result_data = self.tool_functions[func_name](**args)
                                result_str = json.dumps(tool_result_data, indent=2)
                            except Exception as e:
                                result_str = json.dumps({"error": str(e)})
                            
                            # Append result and continue loop
                            from xai_sdk.chat import tool_result
                            self.chat.append(tool_result(result_str))
            
            # If no client-side tools, this is the final response
            if not has_client_tools:
                # Yield the final text content
                if hasattr(response, 'content') and response.content:
                    yield {
                        "type": "text",
                        "content": response.content
                    }
                
                # Yield usage information for cost tracking
                if hasattr(response, 'usage'):
                    yield {
                        "type": "usage",
                        "usage": {
                            "input_tokens": response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else 0,
                            "output_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0
                        }
                    }
                
                # Extract server-side tool usage
                if hasattr(response, 'tool_usage') and response.tool_usage:
                    for tool_name, count in dict(response.tool_usage).items():
                        yield {
                            "type": "tool_call",
                            "tool": tool_name,
                            "arguments": {"note": f"Server-side tool executed {count}x"}
                        }
                
                break
            
            iteration += 1
        
        # Mark completion
        yield {"type": "complete"}
    
    def send_message_sync(self, message: str) -> Dict[str, Any]:
        """Send a message and get complete response (non-streaming).
        
        Handles both server-side tool calls (automatic) and client-side tool calls
        (CDLI + Image, executed locally and results appended to chat).
        
        Args:
            message: User message
            
        Returns:
            Dict with response content and metadata
        """
        self.chat.append(user(message))
        
        # Tool execution loop - continue until we get a final text response
        max_iterations = 10
        iteration = 0
        tool_calls_made = []
        
        while iteration < max_iterations:
            response = self.chat.sample()
            
            # Check for client-side tool calls
            has_client_tool = False
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    if get_tool_call_type(tool_call) == "client_side_tool":
                        has_client_tool = True
                        func_name = tool_call.function.name
                        tool_calls_made.append(func_name)
                        
                        if func_name in self.tool_functions:
                            # Parse arguments
                            try:
                                args = json.loads(tool_call.function.arguments)
                            except json.JSONDecodeError:
                                args = {}
                            
                            # Execute the tool (CDLI or Image)
                            try:
                                tool_result_data = self.tool_functions[func_name](**args)
                                result_str = json.dumps(tool_result_data, indent=2)
                            except Exception as e:
                                result_str = json.dumps({"error": str(e)})
                            
                            # Append tool result
                            from xai_sdk.chat import tool_result
                            self.chat.append(tool_result(result_str))
            
            # If no client-side tools were called, we have final response
            if not has_client_tool:
                break
            
            iteration += 1
        
        # Extract final response content and tool usage
        tool_usage = {}
        if hasattr(response, 'tool_usage') and response.tool_usage:
            tool_usage = dict(response.tool_usage)
        
        # Add client-side tool calls to usage tracking
        if tool_calls_made:
            for tool_name in tool_calls_made:
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        return {
            "content": response.content if hasattr(response, 'content') else "",
            "tool_usage": tool_usage,
            "usage": {
                "input_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                "output_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0
            }
        }
