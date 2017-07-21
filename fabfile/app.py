#!/usr/bin/env python
# -*- coding: utf-8 -*-
from configure import ConfigTask
from fabric.api import sudo, env, cd, task, settings


def _venv(cmd):
    """
    A wrapper for running commands inside the virturalenv
    """
    with cd(env.repo_dir):
        sudo(
            "{} && {}".format(env.activate, cmd),
            user=env.app_user
        )


@task(task_class=ConfigTask)
def rmpyc():
    """
    Erases pyc files from the app's code directory.
    """
    with cd(env.repo_dir):
        sudo("find . -name '*.pyc' -print0|xargs -0 rm", pty=True)


@task(task_class=ConfigTask)
def pipinstall():
    """
    Install the Python requirements inside the virtualenv
    """
    _venv("pip install -r requirements.txt --upgrade --log-file=/tmp/pip.log")


@task(task_class=ConfigTask)
def pull():
    """
    Pull the lastest changes from the GitHub repo
    """
    if env.config_section == "DEV":
        env.branch = 'development'
    else:
        env.branch = 'master'
    _venv('git pull origin {}'.format(env.branch))


@task(task_class=ConfigTask)
def manage(cmd):
    """
    Run a manage.py command inside the Django virtualenv
    """
    _venv("python manage.py %s" % cmd)


@task(task_class=ConfigTask)
def build():
    """
    Run django-bakery's `build` command
    """
    _venv("python manage.py build")


@task(task_class=ConfigTask)
def publish():
    """
    Run django-bakery's `publish` command
    """
    _venv("python manage.py publish")


@task(task_class=ConfigTask)
def migrate():
    """
    Run Django's `migrate` command
    """
    _venv("python manage.py migrate")


@task(task_class=ConfigTask)
def collectstatic():
    """
    Roll out the Django app's latest static files
    """
    _venv("rm -rf ./static")
    _venv("python manage.py collectstatic --noinput")


@task(task_class=ConfigTask)
def compress():
    """
    Run django-compressor's `compress` command
    """
    _venv("python manage.py compress --force")


@task(task_class=ConfigTask)
def deploy():
    """
    Run a full deployment of code to the remote server
    """
    pull()
    with settings(warn_only=True):
        rmpyc()
    pipinstall()
    migrate()
    compress()
    collectstatic()
    build()
    publish()
