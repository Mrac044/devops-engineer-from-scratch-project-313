run:
	uv run flask --app scripts/app run --port 8080
debug:
	uv run flask --app scripts/app --debug run --port 8080