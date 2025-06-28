# Makefile
# This Makefile provides common commands for developing and deploying the project.

# Define variables
PYTHON_EXEC = python3
PIP_EXEC = pip
VENV_DIR = venv
REQUIREMENTS_FILE = requirements.txt
DOCS_DIR = docs # Assuming your main markdown docs are here, or adjust to where index.md is
MKDOCS_CONFIG = mkdocs.yml
TEST_CMD = pytest

.PHONY: all setup install lint test docs deploy clean

all: install test docs # Default target: install, test, then build docs

setup: # Create and activate virtual environment, then install dependencies
	@echo "Setting up virtual environment and installing dependencies..."
	@$(PYTHON_EXEC) -m venv $(VENV_DIR)
	@source $(VENV_DIR)/bin/activate && $(PIP_EXEC) install -r $(REQUIREMENTS_FILE)
	@echo "Setup complete. Run 'source $(VENV_DIR)/bin/activate' to activate the environment."

install: # Install Python dependencies
	@echo "Installing Python dependencies..."
	@source $(VENV_DIR)/bin/activate && $(PIP_EXEC) install -r $(REQUIREMENTS_FILE)

lint: # Run linting checks (e.g., flake8, black, isort)
	@echo "Running linting checks..."
	@source $(VENV_DIR)/bin/activate && flake8 .
	@echo "Linting complete."

test: # Run unit and integration tests
	@echo "Running tests..."
	@source $(VENV_DIR)/bin/activate && $(TEST_CMD)
	@echo "Tests complete."

docs: # Build the documentation using MkDocs
	@echo "Building documentation..."
	@source $(VENV_DIR)/bin/activate && mkdocs build -f $(MKDOCS_CONFIG)
	@echo "Documentation built in the 'site' directory."

serve-docs: # Serve the documentation locally
	@echo "Serving documentation locally..."
	@source $(VENV_DIR)/bin/activate && mkdocs serve -f $(MKDOCS_CONFIG)

deploy: # Placeholder for deployment command (e.g., Docker build, cloud deployment)
	@echo "Initiating deployment..."
	# Add your specific deployment commands here
	# Example: docker build -t ah_reco_llm .
	# Example: aws s3 sync site/ s3://your-docs-bucket --delete
	@echo "Deployment process finished."

clean: # Clean up generated files and directories
	@echo "Cleaning up build artifacts and virtual environment..."
	@rm -rf $(VENV_DIR)
	@rm -rf __pycache__
	@find . -name "*.pyc" -exec rm -f {} +
	@find . -name "*.bak" -exec rm -f {} +
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf site # MkDocs output directory
	@rm -f generated_email.html # Generated email file
	@echo "Clean up complete."

