# Desert Agriculture Sentinel - Makefile

.PHONY: help install install-dev test lint format clean run-example train-models download-data water-report docker-build docker-run

# Default help command
help:
	@echo "Desert Agriculture Sentinel - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      - Install project dependencies"
	@echo "  install-dev  - Install project and development dependencies"
	@echo "  clean        - Clean up temporary files and caches"
	@echo ""
	@echo "Development Commands:"
	@echo "  test         - Run unit tests"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black and isort"
	@echo ""
	@echo "Application Commands:"
	@echo "  run-example  - Run example monitoring cycle"
	@echo "  train-models - Train machine learning models"
	@echo "  water-report - Generate water usage report"
	@echo ""
	@echo "Data Commands:"
	@echo "  download-data - Download satellite data"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run application in Docker container"

# Installation
install:
	@echo "Installing Desert Agriculture Sentinel..."
	pip install -r requirements.txt
	@echo "Installation complete!"

install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install -e .
	@echo "Development installation complete!"

# Testing and Quality
test:
	@echo "Running tests..."
	python -m pytest tests/ -v --cov=src/

lint:
	@echo "Running code linting..."
	flake8 src/ scripts/ main.py
	mypy src/ scripts/ main.py

format:
	@echo "Formatting code..."
	black src/ scripts/ main.py
	isort src/ scripts/ main.py

# Application Commands
run-example:
	@echo "Running example monitoring cycle..."
	python main.py

train-models:
	@echo "Training machine learning models..."
	python scripts/train_models.py --generate-sample-data --samples 1000

water-report:
	@echo "Generating water usage report..."
	python scripts/water_report.py --area-hectares 10 --crop-type wheat

download-data:
	@echo "Downloading sample data..."
	python scripts/download_data.py --area "31.5,31.3,35.2,35.0" --start-date "2025-01-01" --end-date "2025-01-31"

# Cleanup
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name ".coverage" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .tox/
	@echo "Cleanup complete!"

# Create necessary directories
setup-dirs:
	@echo "Creating project directories..."
	mkdir -p data/raw data/processed data/sentinel2 data/landsat
	mkdir -p models logs results
	@echo "Directories created!"

# Initialize project
init: setup-dirs install
	@echo "Initializing Desert Agriculture Sentinel project..."
	python -c "from src.config import Config; Config('config/config.yaml').save_config()"
	@echo "Project initialization complete!"
	@echo "Edit config/config.yaml with your satellite API credentials"

# Quick start
quickstart: init train-models
	@echo "Quick start setup complete!"
	@echo "You can now run: make run-example"

# Docker commands (optional)
docker-build:
	@echo "Building Docker image..."
	docker build -t desert-agriculture-sentinel .

docker-run:
	@echo "Running Docker container..."
	docker run -it --rm -v $$(pwd)/data:/app/data desert-agriculture-sentinel

# Documentation (if you add docs later)
docs:
	@echo "Building documentation..."
	cd docs && make html

# Full workflow example
example-workflow: init train-models run-example water-report
	@echo "Complete example workflow executed!"
