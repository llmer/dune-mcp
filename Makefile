# Dune MCP Server Makefile

.PHONY: install run test clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  install    - Install project dependencies"
	@echo "  run        - Run the MCP server"
	@echo "  test       - Run the test client"
	@echo "  clean      - Clean build artifacts"
	@echo "  help       - Show this help message"

# Install dependencies
install:
	@echo "Installing dependencies with uv..."
	uv install
	@echo "Installation complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy .env.example to .env: cp .env.example .env"
	@echo "2. Add your Dune API key to .env"
	@echo "3. Run the server: make run"

# Run the MCP server
run:
	@echo "Starting Dune MCP Server..."
	@echo "Make sure you have set DUNE_API_KEY in your .env file"
	uv run python main.py

# Run test client
test:
	@echo "Running test client..."
	uv run python test_client.py

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	@echo "Clean complete!"