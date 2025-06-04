from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn
import os
from mcp.server.fastmcp import FastMCP
from mcp_instance import mcp

# Import all modules that contain tools
import k8s_client
import k8s_deployments
import k8s_services
import k8s_replicasets
import k8s_pods

import asyncio

async def print_tools():
    tools = await mcp.list_tools()
    print("Available tools:", tools)

if __name__ == "__main__":
    asyncio.run(print_tools())
    host = os.getenv("HOST", "0.0.0.0")  # Use 0.0.0.0 to allow external connections
    port = int(os.getenv("PORT", "8080"))
    print(f"Starting MCP server on {host}:{port}")
    uvicorn.run(mcp.streamable_http_app, host=host, port=port) 