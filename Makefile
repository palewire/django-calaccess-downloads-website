.PHONY: test

test:
	flake8 fabfile
	flake8 calaccess_website
	flake8 project
	coverage run manage.py test calaccess_website

rs:
	python manage.py runserver

sh:
	python manage.py shell
