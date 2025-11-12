.PHONY: help setup build start stop restart logs status clean test health

help: ## Show this help message
	@echo "Tardis Download Service - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Run initial setup (create .env and directories)
	@chmod +x setup.sh
	@./setup.sh

build: ## Build Docker containers
	docker-compose build

start: ## Start the service
	docker-compose up -d
	@echo ""
	@echo "Service started! Check status with: make status"

stop: ## Stop the service
	docker-compose down

restart: ## Restart the service
	docker-compose restart

logs: ## Show live logs
	docker-compose logs -f

status: ## Check service status
	@docker-compose ps
	@echo ""
	@echo "Health check:"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Service not responding"

clean: ## Stop and remove all containers, volumes
	docker-compose down -v
	@echo "Cleaned up containers and volumes"

test: ## Test the API
	@echo "Testing health endpoint..."
	@curl -s http://localhost:8000/health
	@echo ""
	@echo ""
	@echo "Testing API documentation..."
	@curl -s http://localhost:8000/docs >/dev/null && echo "API docs available at http://localhost:8000/docs" || echo "Service not responding"

health: ## Check service health
	@curl -s http://localhost:8000/health | python -m json.tool

dev-logs: ## Show detailed logs (last 100 lines)
	docker-compose logs --tail=100

backup-db: ## Backup the database
	@mkdir -p backups
	@cp data/downloads.db backups/downloads.db.$(shell date +%Y%m%d_%H%M%S)
	@echo "Database backed up to backups/"

client: ## Show client usage examples
	@echo "Client Usage Examples:"
	@echo ""
	@echo "1. Submit download:"
	@echo "   python client.py --exchange binance --symbols BTC-USDT --start-date 2024-01-01 --end-date 2024-01-02"
	@echo ""
	@echo "2. Check job status:"
	@echo "   python client.py --job-id 123"
	@echo ""
	@echo "3. List jobs:"
	@echo "   python client.py --list-jobs"