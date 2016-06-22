from fabric.api import local, task, sudo, cd, env


@task
def rs(port=8000):
    """
    Start up the Django runserver.
    """
    local("python cacivicdata/manage.py runserver 0.0.0.0:%s" % port)


@task
def git_pull():
    """
    Pull the lastest changes from the GitHub repo
    """
    with cd('/apps/calaccess/repo'):
        sudo(
            'git pull origin master',
            user=env.app_user
        )
