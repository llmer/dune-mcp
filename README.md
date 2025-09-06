# Dune Analytics MCP Server

An MCP (Model Context Protocol) server that exposes Dune Analytics functionality, allowing AI assistants to interact with Dune's blockchain analytics platform.

## Features

This MCP server provides the following tools:

### Query Management
- **get_query**: Retrieve detailed information about a query by ID
- **execute_query**: Run a query and get results  
- **create_query**: Create new Dune queries
- **get_latest_query_result**: Get cached results without re-execution

### Table/Materialized Views
- **create_table**: Create new tables with custom schema
- **upload_csv_to_table**: Upload CSV data to create tables

### Query Building
- **query_builder_helper**: Generate Dune v2 SQL templates with proper syntax

## Setup

### Quick Start with Make

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Dune API key
   ```

3. **Run the MCP server:**
   ```bash
   make run
   ```

### Manual Setup

1. **Install dependencies:**
   ```bash
   uv install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file or export directly:
   export DUNE_API_KEY="your_dune_api_key_here"
   ```
   
   Get your API key from [Dune Analytics Settings](https://dune.com/settings/api).

3. **Run the MCP server:**
   ```bash
   uv run python main.py
   ```

## Usage

### With Claude Code

Use the MCP server directly with Claude Code by running:

```bash
# Start the server
uv run python main.py

# Then in Claude Code, the server will be automatically available
# You can interact with Dune Analytics through natural language:
```

Example interactions:
- "Get information about Dune query 1234567"
- "Execute query 5678 with blockchain parameter set to ethereum"
- "Help me create a query to analyze DEX volume for the past week"
- "Build a SQL template for tracking token holder changes"

### With Cursor

Add to your Cursor MCP configuration in settings:

```json
{
  "mcp": {
    "servers": {
      "dune-analytics": {
        "command": "uv",
        "args": ["run", "python", "/absolute/path/to/dune-mcp/main.py"],
        "env": {
          "DUNE_API_KEY": "your_api_key_here"
        }
      }
    }
  }
}
```

### With Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "dune-analytics": {
      "command": "uv",
      "args": ["run", "python", "/path/to/dune-mcp/main.py"],
      "env": {
        "DUNE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Testing

Run the test client to verify functionality:

```bash
make test
# or manually:
uv run python test_client.py
```

## Example Usage

Once connected via MCP, you can:

1. **Query existing Dune queries:**
   ```
   Get information about query 1234567
   ```

2. **Execute queries with parameters:**
   ```
   Run query 1234567 with parameter "blockchain" set to "ethereum"
   ```

3. **Create new queries:**
   ```
   Create a query to get the top 10 token holders for a specific contract
   ```

4. **Build SQL templates:**
   ```
   Help me write a Dune query to analyze DEX trading volume over time
   ```

## Supported Use Cases

- **Query Discovery**: Retrieve and analyze existing saved queries
- **Query Execution**: Run queries with custom parameters  
- **Table Creation**: Create materialized views from data
- **SQL Generation**: Generate proper Dune v2 SQL syntax
- **Data Analysis**: Process blockchain data through Dune's infrastructure

## Requirements

- Python 3.11+
- Dune Analytics API key
- Plus subscription for query creation and table operations