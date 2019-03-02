all: maj dev

dev:
	python manage.py runserver
maj:
	pip install -r requirements.txt
