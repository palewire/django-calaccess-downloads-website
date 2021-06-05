release: chmod u+x release.sh && ./release.sh
web: gunicorn wsgi:application --log-file -
update: python manage.py updatecalaccessrawdata --verbosity=3
