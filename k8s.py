from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("k8s mcp server", "0.1.0")

# Constants
K8S_API_BASE = "https://kubernetes.api"

@mcp.tool("get_deployment")
def get_deployment(name: str, namespace: str = "default") -> Any:
    url = f"{K8S_API_BASE}/apis/apps/v1/namespaces/{namespace}/deployments/{name}"
    headers = {"User-Agent": "k8s-app/1.0"}
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    mcp.run("stdio")