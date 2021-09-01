.PHONY: test

test:
	pipenv run flake8 calaccess_website  --exclude=calaccess_website/migrations/*
	pipenv run flake8 project
	pipenv run coverage run manage.py test calaccess_website

rs:
	python manage.py runserver

sh:
	python manage.py shell

hack:
	python manage.py archivecalaccessfilingsfile Form460Filing;
	python manage.py archivecalaccessfilingsfile Form460ScheduleAItem;
	python manage.py archivecalaccessfilingsfile Form460ScheduleCItem;
	python manage.py archivecalaccessfilingsfile Form460ScheduleEItem;
	python manage.py archivecalaccessfilingsfile Form460ScheduleB1Item;
	python manage.py archivecalaccessfilingsfile Form497Filing;
	python manage.py archivecalaccessfilingsfile Form497Part1Item;
	python manage.py archivecalaccessfilingsfile Form460ScheduleASummary;
	python manage.py archivecalaccessfilingsfile Form460ScheduleCSummary;
	python manage.py archivecalaccessfilingsfile Form460ScheduleESummary;
