run:
	uv run flask --app paas/scripts/app run --port 8080

debug:
	uv run flask --app paas/scripts/app --debug run --port 8080

lint:
	uv run ruff check paas

test:
	uv run pytest