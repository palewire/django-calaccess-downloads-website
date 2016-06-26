#!/usr/bin/env python
# -*- coding: utf-8 -*-
from configure import ConfigTask
from fabric.api import sudo, env, cd, task

#
# System commands
#


@task(task_class=ConfigTask)
def rmpyc():
    """
    Erases pyc files from the app's code directory.
    """
    env.shell = "/bin/bash -c"
    with cd(env.project_dir):
        sudo("find . -name '*.pyc' -print0|xargs -0 rm", pty=True)

#
# Python commands
#


@task(task_class=ConfigTask)
def pipinstall():
    """
    Install the Python requirements inside the virtualenv
    """
    _venv("pip install -r requirements.txt")


def _venv(cmd):
    """
    A wrapper for running commands inside the virturalenv
    """
    with cd(env.project_dir):
        sudo(
            "%s && %s" % (env.activate, cmd),
            user=env.app_user
        )


@task(task_class=ConfigTask)
def pull():
    """
    Pull the lastest changes from the GitHub repo
    """
    with cd(env.repo_dir):
        sudo(
            'git pull origin {}'.format(env.branch),
            user=env.app_user
        )


@task(task_class=ConfigTask)
def manage(cmd):
    """
    Run a manage.py command inside the Django virtualenv
    """
    _venv("python manage.py %s" % cmd)


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
