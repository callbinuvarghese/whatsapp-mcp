#!/usr/bin/env python3
"""
MCP Client to list available API calls from a local stdio server.
This script connects to an MCP server and displays all available tools, resources, and prompts.
"""

import asyncio
import json
import sys
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import Tool, Resource, Prompt
except ImportError:
    print("Error: MCP library not found. Install with: pip install mcp")
    sys.exit(1)


class MCPClientInspector:
    """Client to inspect MCP server capabilities."""
    
    def __init__(self, server_command: str, server_args: list = None, server_env: dict = None):
        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args or [],
            env=server_env
        )
    
    @asynccontextmanager
    async def connect(self):
        """Connect to the MCP server."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                try:
                    # Initialize the connection
                    init_result = await session.initialize()
                    print(f"✓ Connected to server: {init_result.serverInfo.name}")
                    print(f"  Version: {init_result.serverInfo.version}")
                    print(f"  Protocol Version: {init_result.protocolVersion}\n")
                    yield session
                except Exception as e:
                    print(f"✗ Failed to initialize session: {e}")
                    raise
    
    async def list_tools(self, session: ClientSession) -> None:
        """List all available tools."""
        try:
            tools_result = await session.list_tools()
            tools = tools_result.tools if hasattr(tools_result, 'tools') else []
            
            print("🔧 AVAILABLE TOOLS:")
            print("=" * 50)
            
            if not tools:
                print("  No tools available")
                return
            
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.name}")
                if hasattr(tool, 'description') and tool.description:
                    print(f"   Description: {tool.description}")
                
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    print(f"   Input Schema:")
                    self._print_schema(tool.inputSchema, indent=6)
                print()
                
        except Exception as e:
            print(f"✗ Error listing tools: {e}")
    
    async def list_resources(self, session: ClientSession) -> None:
        """List all available resources."""
        try:
            resources_result = await session.list_resources()
            resources = resources_result.resources if hasattr(resources_result, 'resources') else []
            
            print("📁 AVAILABLE RESOURCES:")
            print("=" * 50)
            
            if not resources:
                print("  No resources available")
                return
            
            for i, resource in enumerate(resources, 1):
                print(f"{i}. {resource.uri}")
                if hasattr(resource, 'name') and resource.name:
                    print(f"   Name: {resource.name}")
                if hasattr(resource, 'description') and resource.description:
                    print(f"   Description: {resource.description}")
                if hasattr(resource, 'mimeType') and resource.mimeType:
                    print(f"   MIME Type: {resource.mimeType}")
                print()
                
        except Exception as e:
            print(f"✗ Error listing resources: {e}")
    
    async def list_prompts(self, session: ClientSession) -> None:
        """List all available prompts."""
        try:
            prompts_result = await session.list_prompts()
            prompts = prompts_result.prompts if hasattr(prompts_result, 'prompts') else []
            
            print("💬 AVAILABLE PROMPTS:")
            print("=" * 50)
            
            if not prompts:
                print("  No prompts available")
                return
            
            for i, prompt in enumerate(prompts, 1):
                print(f"{i}. {prompt.name}")
                if hasattr(prompt, 'description') and prompt.description:
                    print(f"   Description: {prompt.description}")
                
                if hasattr(prompt, 'arguments') and prompt.arguments:
                    print(f"   Arguments:")
                    for arg in prompt.arguments:
                        print(f"     - {arg.name}: {arg.description}")
                        if hasattr(arg, 'required') and arg.required:
                            print(f"       (required)")
                print()
                
        except Exception as e:
            print(f"✗ Error listing prompts: {e}")
    
    def _print_schema(self, schema: Dict[str, Any], indent: int = 0) -> None:
        """Pretty print a JSON schema."""
        indent_str = " " * indent
        
        if isinstance(schema, dict):
            schema_type = schema.get('type', 'unknown')
            print(f"{indent_str}Type: {schema_type}")
            
            if 'properties' in schema:
                print(f"{indent_str}Properties:")
                for prop_name, prop_schema in schema['properties'].items():
                    print(f"{indent_str}  {prop_name}:")
                    self._print_schema(prop_schema, indent + 4)
            
            if 'required' in schema:
                print(f"{indent_str}Required: {', '.join(schema['required'])}")
                
            if 'description' in schema:
                print(f"{indent_str}Description: {schema['description']}")
        else:
            print(f"{indent_str}{schema}")
    
    async def inspect_server(self) -> None:
        """Inspect all server capabilities."""
        try:
            async with self.connect() as session:
                await self.list_tools(session)
                print("\n")
                await self.list_resources(session)
                print("\n")
                await self.list_prompts(session)
                
        except Exception as e:
            print(f"✗ Error connecting to server: {e}")


async def main():
    """Main function to run the MCP client inspector."""
    
    # Example configurations - modify these for your server
    examples = {
        # "python_server": {
        #     "command": "python",
        #     "args": ["path/to/your/mcp_server.py"],
        #     "description": "Python MCP server"
        # },
        "node_server": {
            "command": "node",
            "args": ["/Users/binu.b.varghese/source/agent/whatsapp/whatsapp-mcp-ts/src/main.ts"],
            "description": "Node.js MCP server"
        },
        # "binary_server": {
        #     "command": "./path/to/mcp_server_binary",
        #     "args": [],
        #     "description": "Compiled MCP server binary"
        # }
    }
    
    # Configuration for your TypeScript MCP server
    SERVER_COMMAND = "node"
    SERVER_ARGS = ["/Users/binu.b.varghese/source/agent/whatsapp/whatsapp-mcp-ts/src/main.ts"]  # your TypeScript server entry point
    SERVER_ENV = {
        # Add any environment variables your WhatsApp MCP server needs
        # "WHATSAPP_TOKEN": "your_token",
        # "DEBUG": "true"
    }
    
    print("MCP Server API Inspector")
    print("=" * 50)
    print(f"Connecting to server: {SERVER_COMMAND} {' '.join(SERVER_ARGS)}")
    print()
    
    inspector = MCPClientInspector(
        server_command=SERVER_COMMAND,
        server_args=SERVER_ARGS,
        server_env=SERVER_ENV
    )
    
    await inspector.inspect_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)