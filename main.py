from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn
from mcp_instance import mcp

# Import all Kubernetes tool modules
import k8s_client
import k8s_deployments

# Create Starlette app
app = Starlette(
    routes=[
        Mount("/", app=mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080) 