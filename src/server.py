"""
MCP Server main entry point
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import tools and resources
from src.tools import register_tools
from src.resources import register_resources


async def main():
    # Create server instance
    server = Server("nonpayment-health")
    
    # Register tools and resources
    register_tools(server)
    register_resources(server)
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

