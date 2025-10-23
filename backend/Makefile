# Makefile for Backend Docker Operations

# Variables
IMAGE_NAME = microlearning-backend
CONTAINER_NAME = microlearning-backend
PORT = 4000
TAG = latest

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

.PHONY: help build run stop clean logs shell test health push dev prod

help: ## Show this help message
	@echo "$(GREEN)Microlearning Backend - Docker Commands$(NC)"
	@echo "========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Build the Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(IMAGE_NAME):$(TAG) .

run: ## Run the container
	@echo "$(GREEN)Starting container...$(NC)"
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):$(PORT) \
		--env-file .env \
		$(IMAGE_NAME):$(TAG)

dev: ## Run container in development mode with volume mounts
	@echo "$(GREEN)Starting in development mode...$(NC)"
	docker run -d \
		--name $(CONTAINER_NAME)-dev \
		-p $(PORT):$(PORT) \
		--env-file .env \
		-v $(PWD):/app \
		$(IMAGE_NAME):$(TAG)

stop: ## Stop the running container
	@echo "$(YELLOW)Stopping container...$(NC)"
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker stop $(CONTAINER_NAME)-dev 2>/dev/null || true

clean: stop ## Stop and remove container and image
	@echo "$(RED)Removing container and image...$(NC)"
	docker rm $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME)-dev 2>/dev/null || true
	docker rmi $(IMAGE_NAME):$(TAG) 2>/dev/null || true

logs: ## Show container logs
	@echo "$(GREEN)Container logs:$(NC)"
	docker logs -f $(CONTAINER_NAME)

shell: ## Open a shell in the running container
	@echo "$(GREEN)Opening shell...$(NC)"
	docker exec -it $(CONTAINER_NAME) /bin/bash

test: ## Run tests in container
	@echo "$(GREEN)Running tests...$(NC)"
	docker run --rm \
		--env-file .env \
		$(IMAGE_NAME):$(TAG) \
		python -m pytest tests/

health: ## Check health status
	@echo "$(GREEN)Health check:$(NC)"
	@curl -s http://localhost:$(PORT)/healthz | python -m json.tool || echo "$(RED)Service not healthy or not running$(NC)"

push: build ## Build and push to registry (set REGISTRY variable)
	@echo "$(GREEN)Pushing to registry...$(NC)"
	docker tag $(IMAGE_NAME):$(TAG) $(REGISTRY)/$(IMAGE_NAME):$(TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)

# Docker Compose commands
up: ## Start services with docker-compose
	@echo "$(GREEN)Starting with docker-compose...$(NC)"
	docker-compose up -d

down: ## Stop services with docker-compose
	@echo "$(YELLOW)Stopping docker-compose services...$(NC)"
	docker-compose down

rebuild: ## Rebuild and restart with docker-compose
	@echo "$(GREEN)Rebuilding with docker-compose...$(NC)"
	docker-compose down
	docker-compose build
	docker-compose up -d

logs-compose: ## Show docker-compose logs
	@echo "$(GREEN)Docker-compose logs:$(NC)"
	docker-compose logs -f
