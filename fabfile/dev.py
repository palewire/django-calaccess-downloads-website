#!/usr/bin/env python
# -*- coding: utf-8 -*-
from configure import ConfigTask, require_input
from fabric.api import local, task, sudo, cd, env


@task
def rs(port=8000):
    """
    Start up the Django runserver.
    """
    local("python cacivicdata/manage.py runserver 0.0.0.0:%s" % port)


@task
def pull():
    """
    Pull the lastest changes from the GitHub repo
    """
    with cd('/apps/calaccess/repo'):
        sudo(
            'git pull origin master',
            user=env.app_user
        )


@task(task_class=ConfigTask)
def ssh(ec2_instance=''):
    """
    Log into the EC2 instance using SSH.
    """
    if not ec2_instance:
        try:
            ec2_instance = env.hosts[0]
        except IndexError:
            ec2_instance = require_input('EC2 Host [Required]:')
    local("ssh %s@%s -i %s" % (env.user, ec2_instance, env.key_filename[0]))
