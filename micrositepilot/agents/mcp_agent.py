import asyncio
import os

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.models.google import Gemini
from textwrap import dedent
from pydantic import BaseModel, Field
from pathlib import Path

# Get the root directory of the project (parent of micrositepilot)
root_path = str(Path(__file__).parent.parent.parent)
microsites_path = str(Path(root_path) / "microsites")


# Response model for saved HTML content
class HtmlContent(BaseModel):
    content: str = Field(
        ..., description="The HTML content that was saved to the filesystem."
    )


async def run_agent(html_site, audio_source: str = None):
    env = {
        **os.environ,
        "NETLIFY_PERSONAL_ACCESS_TOKEN": os.getenv("NETLIFY_PERSONAL_ACCESS_TOKEN"),
    }

    async with MCPTools(
        f"npx -y @modelcontextprotocol/server-filesystem {microsites_path}"
    ) as mcp_tools:
        microsite_builder_agent = Agent(
            model=Gemini(id="gemini-2.0-flash-001", response_modalities=["text"]),
            description=dedent(
                """\
                Saves HTML microsite content to the filesystem using MCP tools.
                Takes pre-generated HTML code and saves it to the /microsites directory
                with proper file naming conventions."""
            ),
            instructions=dedent(
                f"""\
                You MUST save the provided HTML content to a file in the microsites directory.

                **Your Task:**
                1. Take the provided HTML content
                2. Save it to a file using the write_file tool
                3. Use filename format: demo_20250601_143000.html (with current timestamp)

                **REQUIRED ACTION:**
                You MUST use the write_file tool to save the HTML content to a file named "index-{{timestamp}}.html".
                
                **Input HTML Content:**
                The user will provide HTML content that you need to save.

                **Process:**
                1. Use write_file tool with filename "demo_test.html" 
                2. Set the content to the provided HTML
                3. Confirm the file was saved

                You MUST call the write_file tool before responding.
                """
            ),
            tools=[mcp_tools],
            show_tool_calls=True,
        )
        await microsite_builder_agent.arun(html_site, audio_source)
