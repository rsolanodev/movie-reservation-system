check:
	uv run mypy app
	uv run ruff check app
	uv run ruff format app --check

format:
	uv run ruff check app --fix
	uv run ruff format app

tests:
	uv run pytest app
