all: clean maj compile-scss dev

dev:
	python manage.py runserver

maj:
	pip install -r requirements.txt

compile-scss:
	sass .\synaiapp\static\sass\app.scss .\synaiapp\static\css\main.css

clean:
	del /s .\static\*.css, .\static\*.map

scss: clean compile-scss
