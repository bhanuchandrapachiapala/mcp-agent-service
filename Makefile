# Development commands for MCP Agent Service

# Use the active Python environment by default.
# Override with: make PYTHON=.venv/Scripts/python.exe test
PYTHON ?= python

.PHONY: help run test lint

help:
	@echo "Available commands:"
	@echo "  make run   - Start the FastAPI development server"
	@echo "  make test  - Run all automated tests"
	@echo "  make lint  - Check Python code with Ruff"

run:
	$(PYTHON) -m uvicorn src.api.main:app --reload

test:
	$(PYTHON) -m pytest -v

lint:
	$(PYTHON) -m ruff check .