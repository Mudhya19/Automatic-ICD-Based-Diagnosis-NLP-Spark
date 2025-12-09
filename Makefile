# Makefile for Automated ICD Diagnosis Extraction Project

# Variables
DOCKER_COMPOSE=docker-compose
JUPYTER=jupyter
PYTHON=python3

.PHONY: help setup install run jupyter clean docker-up docker-down test

help:
	@echo "Available commands:"
	@echo "  setup      - Setup virtual environment and install dependencies"
	@echo "  install    - Install Python dependencies"
	@echo "  run        - Run the automated ICD diagnosis extraction notebook"
	@echo "  jupyter    - Start Jupyter notebook server"
	@echo "  docker-up  - Start services with Docker Compose"
	@echo "  docker-down - Stop services with Docker Compose"
	@echo "  clean      - Clean temporary files and logs"

setup:
	python3 -m venv venv
	bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	bash -c "source venv/bin/activate && jupyter nbconvert --to notebook --execute automated_icd_diagnosis.ipynb"

jupyter:
	bash -c "source venv/bin/activate && jupyter notebook"

docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

clean:
	rm -rf output/*.csv output/*.json output/logs/*
	rm -rf .pytest_cache __pycache__ .coverage
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete