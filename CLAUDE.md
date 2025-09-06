# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project builds an MCP (Model Context Protocol) server that exposes the Dune Analytics SDK, allowing LLM clients to interact with Dune's blockchain analytics platform through standardized MCP tools.

**Key Technologies:**
- Python 3.11+ with uv package management
- `dune-client` - Official Dune Analytics API client
- `pydantic-ai-slim[mcp]` - MCP server framework with Pydantic AI integration

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv install

# Activate virtual environment
source .venv/bin/activate
```

### Running the MCP Server
```bash
# Run the server via stdio (standard MCP communication)
python main.py

# For development with auto-reload
uv run python main.py
```

### Linting and Testing
```bash
# Format code (add when configured)
# uv run black .

# Type checking (add when configured) 
# uv run mypy .

# Run tests (add when test framework is configured)
# uv run pytest
```

## Architecture

### MCP Server Structure
The project follows the FastMCP pattern from Pydantic AI:
- `main.py` - Entry point for the MCP server
- Server runs over stdio for standard MCP client communication
- Tools are defined using the `@server.tool()` decorator

### Dune Integration
- Requires `DUNE_API_KEY` environment variable for authentication
- Uses `DuneClient.from_env()` for client initialization
- Supports query execution, result retrieval, and query management operations

### Expected Tool Categories
Based on the Dune Analytics SDK, the MCP server should expose tools for:
- **Query Execution**: Run queries with parameters, get results as DataFrame/CSV
- **Query Management**: Create, update, archive/unarchive queries
- **Result Retrieval**: Get latest results with age limits to avoid unnecessary re-execution
- **Query Discovery**: Search and explore existing queries

## Environment Configuration

Set up required environment variables:
```bash
export DUNE_API_KEY="your_dune_api_key_here"
```

## MCP Client Testing

Test the server using the Python MCP SDK:
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_client():
    server_params = StdioServerParameters(
        command='python', 
        args=['main.py']
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Test tool calls here
```

## Git Commit Style

Use conventional commits without Claude as co-author:
- `feat: add query execution tool`
- `fix: handle missing API key error`
- `docs: update setup instructions`