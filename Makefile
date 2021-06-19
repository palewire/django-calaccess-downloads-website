.PHONY: test

test:
	pipenv run flake8 calaccess_website
	pipenv run flake8 project
	pipenv run coverage run manage.py test calaccess_website

rs:
	python manage.py runserver

sh:
	python manage.py shell
