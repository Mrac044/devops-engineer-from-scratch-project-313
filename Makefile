FRAMEWORK ?= flask

setup:
	npm ci
	uv sync

start:
ifeq ($(FRAMEWORK), flask)
	npx concurrently "uv run flask --app paas/scripts/app run --port 8080" "npx start-hexlet-devops-deploy-crud-frontend"
else
	@echo "ERROR: Unknown framework. Only flask supported."
	@exit 1
endif

start-debug:
	npx concurrently "uv run flask --app paas/scripts/app --debug --port 8080" "npx start-hexlet-devops-deploy-crud-frontend"

run:
	uv run flask --app paas/scripts/app run --host 0.0.0.0 --port 8080

debug:
	uv run flask --app paas/scripts/app --debug run --port 8080

lint:
	uv run ruff check paas

fix_lint:
	uv run ruff check paas --fix

test:
	uv run pytest