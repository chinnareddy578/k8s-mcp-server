# K8s MCP Server

This project is a Model Control Protocol (MCP) server for Kubernetes operations. It provides tools for managing deployments, pods, services, and more.

## Prerequisites

- Python 3.12 or higher
- `uv` package manager
- Minikube (for local Kubernetes development)
- Docker (optional, for containerized deployment)

## Running the MCP Server

### Primary Method: Running Directly

1. **Create a virtual environment:**

   ```sh
   uv venv .venv
   ```

2. **Activate the virtual environment:**

   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```

3. **Install dependencies:**

   ```sh
   uv pip install -e .
   ```

4. **Run the server:**

   ```sh
   python src/main.py
   ```

### Alternative Method: Using Docker (Optional)

1. **Pull the Docker image:**

   ```sh
   docker pull chinnareddy578/k8s-mcp-server
   ```

2. **Run the Docker container:**

   ```sh
   docker run -it \
     -v ${HOME}/.kube:/root/.kube:ro \
     -v ${HOME}/.minikube:/root/.minikube:ro \
     chinnareddy578/k8s-mcp-server
   ```

## Using the MCP Server with MCP Clients

### GitHub Copilot

1. **Configure GitHub Copilot:**

   - Open your GitHub Copilot settings.
   - Add the following configuration:

   ```json
   {
       "servers": {
           "k8s-mcp-server": {
               "command": "python",
               "args": [
                   "src/main.py"
               ]
           }
       }
   }
   ```

   Alternatively, if you prefer using Docker:

   ```json
   {
       "servers": {
           "k8s-mcp-server": {
               "command": "docker",
               "args": [
                   "run",
                   "-i",
                   "--rm",
                   "--init",
                   "-e", "PYTHONUNBUFFERED=1",
                   "-v", "${HOME}/.kube:/root/.kube:ro",
                   "-v", "${HOME}/.minikube:/root/.minikube:ro",
                   "chinnareddy578/k8s-mcp-server"
               ]
           }
       }
   }
   ```

2. **Use GitHub Copilot:**

   - GitHub Copilot will now use the MCP server for code suggestions and completions.

### Claude Desktop

1. **Configure Claude Desktop:**

   - Open Claude Desktop settings.
   - Add the following configuration:

   ```json
   {
       "mcpServers": {
           "k8s-mcp-server": {
               "command": "python",
               "args": [
                   "src/main.py"
               ]
           }
       }
   }
   ```

   Alternatively, if you prefer using Docker:

   ```json
   {
       "mcpServers": {
           "k8s-mcp-server": {
               "command": "docker",
               "args": [
                   "run",
                   "-i",
                   "--rm",
                   "--init",
                   "-e", "PYTHONUNBUFFERED=1",
                   "-v", "${HOME}/.kube:/root/.kube:ro",
                   "-v", "${HOME}/.minikube:/root/.minikube:ro",
                   "chinnareddy578/k8s-mcp-server"
               ]
           }
       }
   }
   ```

2. **Use Claude Desktop:**

   - Claude Desktop will now use the MCP server for code suggestions and completions.

## Troubleshooting

- **Kubernetes Configuration:** Make sure Minikube is running and your kubeconfig is properly set up:
  ```sh
  minikube status
  minikube kubectl -- get pods
  ```

- **Connection Issues:** If using Docker, ensure the container is running and has access to your Kubernetes configuration:
  ```sh
  docker ps
  ```

- **Tool Not Found:** Verify that the tool is registered in your MCP server and the name matches exactly.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
