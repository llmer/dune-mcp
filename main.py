import os
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from dune_client.client import DuneClient
from dune_client.query import QueryBase
from dune_client.types import QueryParameter
from pydantic import BaseModel, Field

# Initialize the MCP server
server = FastMCP('Dune Analytics MCP Server')

# Global DuneClient instance
dune_client: Optional[DuneClient] = None

def get_dune_client() -> DuneClient:
    """Get or create DuneClient instance"""
    global dune_client
    if dune_client is None:
        api_key = os.getenv('DUNE_API_KEY')
        if not api_key:
            raise ValueError("DUNE_API_KEY environment variable is required")
        dune_client = DuneClient.from_env()
    return dune_client

# Pydantic models for input validation
class QueryInfo(BaseModel):
    """Information about a Dune query"""
    query_id: int = Field(description="The ID of the Dune query")
    name: str = Field(description="Name of the query")
    owner: str = Field(description="Owner of the query")
    is_private: bool = Field(description="Whether the query is private")
    sql: str = Field(description="The SQL code of the query")
    parameters: List[Dict[str, Any]] = Field(description="Query parameters")

class ExecuteQueryRequest(BaseModel):
    """Request to execute a query"""
    query_id: int = Field(description="The ID of the query to execute")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Parameters to pass to the query")

class CreateQueryRequest(BaseModel):
    """Request to create a new query"""
    name: str = Field(description="Name for the new query")
    query_sql: str = Field(description="SQL code for the query")
    is_private: bool = Field(default=False, description="Whether the query should be private")
    parameters: Optional[List[Dict[str, str]]] = Field(default=None, description="Query parameters")

class TableInfo(BaseModel):
    """Information about a table"""
    namespace: str = Field(description="The namespace of the table")
    table_name: str = Field(description="Name of the table")
    full_name: str = Field(description="Full table reference (dune.namespace.table_name)")

@server.tool()
async def get_query(query_id: int) -> Dict[str, Any]:
    """
    Retrieve detailed information about a Dune query by its ID.
    Returns query metadata, SQL, parameters, and ownership info.
    """
    try:
        client = get_dune_client()
        query = client.get_query(query_id)
        
        return {
            "query_id": query.base.query_id,
            "name": query.base.name,
            "sql": query.sql,
            "owner": query.meta.owner,
            "is_private": query.meta.is_private,
            "is_archived": query.meta.is_archived,
            "description": query.meta.description,
            "tags": query.meta.tags,
            "version": query.meta.version,
            "engine": query.meta.engine,
            "parameters": [{
                "name": p.key,
                "type": p.type,
                "value": str(p.value) if p.value is not None else None
            } for p in query.base.parameters()],
            "url": query.base.url()
        }
    except Exception as e:
        return {"error": str(e), "query_id": query_id}

@server.tool()
async def execute_query(query_id: int, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a Dune query and return the results.
    Optionally provide parameters to pass to the query.
    """
    try:
        client = get_dune_client()
        
        # Build query parameters if provided
        query_params = []
        if parameters:
            for key, value in parameters.items():
                if isinstance(value, str):
                    query_params.append(QueryParameter.text_type(key, value))
                elif isinstance(value, (int, float)):
                    query_params.append(QueryParameter.number_type(key, value))
                else:
                    query_params.append(QueryParameter.text_type(key, str(value)))
        
        query = QueryBase(
            query_id=query_id,
            name=f"Query {query_id}",
            params=query_params if query_params else None
        )
        
        # Execute the query
        results = client.run_query(query)
        
        return {
            "query_id": query_id,
            "execution_id": results.execution_id,
            "state": results.state,
            "row_count": len(results.result.rows) if results.result else 0,
            "columns": [col.name for col in results.result.metadata.column_names] if results.result else [],
            "rows": results.result.rows[:100] if results.result else [],  # Limit to first 100 rows
            "is_execution_finished": results.is_execution_finished
        }
    except Exception as e:
        return {"error": str(e), "query_id": query_id}

@server.tool()
async def create_query(name: str, query_sql: str, is_private: bool = False, parameters: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Create a new Dune query.
    Returns the created query's ID and metadata.
    """
    try:
        client = get_dune_client()
        
        # Build query parameters if provided
        query_params = []
        if parameters:
            for param in parameters:
                param_type = param.get('type', 'text')
                param_name = param['name']
                param_value = param.get('value', '')
                
                if param_type == 'number':
                    query_params.append(QueryParameter.number_type(param_name, float(param_value) if param_value else 0))
                elif param_type == 'date':
                    query_params.append(QueryParameter.date_type(param_name, param_value))
                elif param_type == 'enum':
                    query_params.append(QueryParameter.enum_type(param_name, param_value))
                else:
                    query_params.append(QueryParameter.text_type(param_name, param_value))
        
        # Create the query
        created_query = client.create_query(
            name=name,
            query_sql=query_sql,
            is_private=is_private,
            params=query_params if query_params else None
        )
        
        return {
            "query_id": created_query.base.query_id,
            "name": created_query.base.name,
            "url": created_query.base.url(),
            "is_private": created_query.meta.is_private,
            "owner": created_query.meta.owner,
            "parameters": [{
                "name": p.key,
                "type": p.type,
                "value": str(p.value) if p.value is not None else None
            } for p in created_query.base.parameters()]
        }
    except Exception as e:
        return {"error": str(e)}

@server.tool()
async def create_table(namespace: str, table_name: str, schema: List[Dict[str, str]], description: str = "", is_private: bool = False) -> Dict[str, Any]:
    """
    Create a new table in Dune (materialized view).
    Schema should be a list of dictionaries with 'name' and 'type' keys.
    """
    try:
        client = get_dune_client()
        
        result = client.create_table(
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            description=description,
            is_private=is_private
        )
        
        return {
            "success": result.success,
            "full_table_name": f"dune.{namespace}.{table_name}",
            "namespace": namespace,
            "table_name": table_name,
            "description": description,
            "is_private": is_private,
            "example_usage": f"SELECT * FROM dune.{namespace}.{table_name}"
        }
    except Exception as e:
        return {"error": str(e)}

@server.tool()
async def upload_csv_to_table(table_name: str, csv_data: str, description: str = "", is_private: bool = False) -> Dict[str, Any]:
    """
    Upload CSV data to create a new table in Dune.
    The CSV should include headers as the first row.
    """
    try:
        client = get_dune_client()
        
        success = client.upload_csv(
            table_name=table_name,
            data=csv_data,
            description=description,
            is_private=is_private
        )
        
        return {
            "success": success,
            "table_name": table_name,
            "full_table_name": f"dune.{table_name}",  # Note: CSV uploads use different naming
            "description": description,
            "is_private": is_private,
            "example_usage": f"SELECT * FROM dune.{table_name}"
        }
    except Exception as e:
        return {"error": str(e)}

@server.tool()
async def get_latest_query_result(query_id: int, max_age_hours: Optional[int] = None) -> Dict[str, Any]:
    """
    Get the latest cached results for a query without re-executing it.
    Optionally specify max_age_hours to re-run if data is too old.
    """
    try:
        client = get_dune_client()
        
        if max_age_hours:
            results = client.get_latest_result(query_id, max_age_hours=max_age_hours)
        else:
            results = client.get_latest_result(query_id)
        
        return {
            "query_id": query_id,
            "execution_id": results.execution_id,
            "state": results.state,
            "row_count": len(results.result.rows) if results.result else 0,
            "columns": [col.name for col in results.result.metadata.column_names] if results.result else [],
            "rows": results.result.rows[:100] if results.result else [],  # Limit to first 100 rows
            "is_execution_finished": results.is_execution_finished,
            "cached": True
        }
    except Exception as e:
        return {"error": str(e), "query_id": query_id}

@server.tool()
async def query_builder_helper(description: str, tables: Optional[List[str]] = None, filters: Optional[str] = None) -> Dict[str, str]:
    """
    Help construct Dune v2 SQL queries with proper syntax and table references.
    Provides template SQL based on description and available tables.
    """
    try:
        # Basic template construction
        if tables:
            # Build FROM clause with proper dune table references
            from_clause = ", ".join([f"dune.{table}" if not table.startswith('dune.') else table for table in tables])
        else:
            from_clause = "-- Specify your tables here (e.g., dune.namespace.table_name)"
        
        # Build basic query template
        template = f"""
-- Dune v2 SQL Query: {description}
SELECT
    -- Select your columns here
    *
FROM {from_clause}
"""
        
        if filters:
            template += f"WHERE\n    {filters}\n"
        
        template += """
-- Optional: Add GROUP BY, ORDER BY, LIMIT clauses
-- ORDER BY column_name
-- LIMIT 1000
"""
        
        tips = [
            "Use 'dune.namespace.table_name' format for user tables/materialized views",
            "Standard blockchain tables: ethereum.transactions, ethereum.blocks, etc.",
            "Use {{parameter_name}} for parameterized queries",
            "Cast numeric fields: CAST(gas_used AS uint256)",
            "Use DATE() functions for time filtering"
        ]
        
        return {
            "template_sql": template,
            "tips": "\\n".join(f"• {tip}" for tip in tips),
            "description": description
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    server.run()
