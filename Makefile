.PHONY: help install dev test lint format typecheck coverage clean build publish docker-build docker-run validate-policy validate-examples

PYTHON := python3
PIP := pip3

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install package in development mode
	$(PIP) install -e .

dev: ## Install package with development dependencies
	$(PIP) install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

lint: ## Run linters
	ruff check src/ tests/
	ruff format --check src/ tests/

format: ## Format code
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck: ## Run type checking
	mypy src/

coverage: ## Run tests with coverage
	pytest tests/ -v --cov=src/api_governor --cov-report=html --cov-report=term

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

build: clean ## Build package
	$(PYTHON) -m build

publish: build ## Publish to PyPI (requires credentials)
	twine upload dist/*

docker-build: ## Build Docker image
	docker build -t api-governor:latest .

docker-run: ## Run Docker container with example
	docker run --rm -v $(PWD)/skills/api-governor/resources/examples:/specs api-governor:latest /specs/openapi_v1.yaml

validate-policy: ## Validate policy files against schema
	$(PYTHON) scripts/validate_policies.py

validate-examples: ## Validate example OpenAPI specs
	$(PYTHON) scripts/validate_openapi.py skills/api-governor/resources/examples/*.yaml

# Example targets
example: ## Run governance on example spec
	$(PYTHON) -m api_governor skills/api-governor/resources/examples/openapi_v1.yaml

example-diff: ## Run governance with baseline comparison
	$(PYTHON) -m api_governor skills/api-governor/resources/examples/openapi_v2_breaking.yaml \
		--baseline skills/api-governor/resources/examples/openapi_v1.yaml

example-strict: ## Run governance with strict policy
	$(PYTHON) -m api_governor skills/api-governor/resources/examples/openapi_v1.yaml --strict

all: lint typecheck test ## Run all checks
