build:
	./build.sh

render-start:
	gunicorn task_manager.wsgi

check:
	uv run ruff check .

check-fix:
	uv run ruff check --fix .

tests:
	python manage.py test