

run:
	protoc --proto_path=proto --python_out=worker/generated proto/*.proto
	poetry run python -m worker

mypy:
	poetry run mypy worker

ruff:
	poetry run ruff check worker --fix
