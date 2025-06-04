from mcp.server.fastmcp import FastMCP

# Create a single shared MCP instance
mcp = FastMCP(name="k8s-server", version="0.1.0")

# Export the instance
__all__ = ['mcp'] 