#!/usr/bin/env python3
"""
Test client for the Dune MCP server.
This demonstrates how to connect to and interact with the MCP server.
"""

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_dune_mcp_server():
    """Test the Dune MCP server by connecting and calling tools."""
    
    # Set up server parameters
    server_params = StdioServerParameters(
        command='python', 
        args=['main.py'],
        env=dict(os.environ, DUNE_API_KEY="test_key_placeholder")
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List available tools
                print("Available tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test query_builder_helper tool
                print("\n--- Testing query_builder_helper ---")
                result = await session.call_tool(
                    'query_builder_helper', 
                    {
                        'description': 'Get top 10 most expensive Ethereum transactions',
                        'tables': ['ethereum.transactions'],
                        'filters': 'gas_used > 1000000'
                    }
                )
                print("Query builder result:")
                print(result.content[0].text if result.content else "No content")
                
                print("\n--- Server connection test completed successfully! ---")
                
    except Exception as e:
        print(f"Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(test_dune_mcp_server())