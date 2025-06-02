from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn
from mcp_instance import mcp
import os

# Import all Kubernetes tool modules
import k8s_client
import k8s_deployments
import k8s_pods
import k8s_services
import k8s_replicasets

# Create Starlette app
app = Starlette(
    routes=[
        Mount("/", app=mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")  # Use 0.0.0.0 to allow external connections
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host=host, port=port) 