release: chmod u+x release.sh && ./release.sh
web: gunicorn wsgi:application --log-file -

updateraw: python manage.py updatecalaccessrawdata --verbosity=3 --noinput
updateprocessed: python manage.py processcalaccessdata --verbosity=3
update: python manage.py updatedownloadswebsite --verbosity=3 --noinput

clock: python clock.py
