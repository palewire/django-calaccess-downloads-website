from fabric.api import local, task


@task
def rs(port=8000):
    """
    Start up the Django runserver.
    """
    local("python cacivicdata/manage.py runserver 0.0.0.0:%s" % port)
