.PHONY: test

test:
	flake8 fabfile
	flake8 calaccess_website
	flake8 project
	coverage run manage.py test --settings=project.settings_test calaccess_website
