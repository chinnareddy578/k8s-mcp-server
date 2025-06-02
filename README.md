# K8s MCP Server

This project is a Model Control Protocol (MCP) server for Kubernetes operations. It provides tools for managing deployments, pods, services, and more.

## Prerequisites

- Docker
- Python 3.12 or higher
- `uv` package manager

## Building and Running the MCP Server

### Using Docker

1. **Build the Docker image:**

   ```sh
   docker build -t k8s-mcp-server .
   ```

2. **Run the Docker container:**

   ```sh
   docker run -p 8080:8080 k8s-mcp-server
   ```

   The server will be accessible at [http://localhost:8080](http://localhost:8080).

### Using Python Directly

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

## Using the MCP Server with MCP Clients

### GitHub Copilot

1. **Configure GitHub Copilot:**

   - Open your GitHub Copilot settings.
   - Set the MCP server URL to `http://localhost:8080`.

2. **Use GitHub Copilot:**

   - GitHub Copilot will now use the MCP server for code suggestions and completions.

### Claude Desktop

1. **Configure Claude Desktop:**

   - Open Claude Desktop settings.
   - Set the MCP server URL to `http://localhost:8080`.

2. **Use Claude Desktop:**

   - Claude Desktop will now use the MCP server for code suggestions and completions.

### Other MCP Clients

For other MCP clients, follow these general steps:

1. **Configure the client:**

   - Set the MCP server URL to `http://localhost:8080`.

2. **Use the client:**

   - The client will now use the MCP server for code suggestions and completions.

## Troubleshooting

- **Connection Issues:** Ensure the Docker container is running and the port is correctly mapped. Check with:
  ```sh
  docker ps
  ```

- **Tool Not Found:** Verify that the tool is registered in your MCP server and the name matches exactly.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
