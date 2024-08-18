check:
	poetry run mypy app
	poetry run ruff check app
	poetry run ruff format app --check

format:
	poetry run ruff check app --fix
	poetry run ruff format app

tests:
	poetry run pytest app
