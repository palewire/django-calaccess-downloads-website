#!/usr/bin/env python
# -*- coding: utf-8 -*-
from configure import ConfigTask
from fabric.operations import prompt
from fabric.api import local, task, env


@task
def rs(port=8000):
    """
    Start up the Django runserver.
    """
    local("python manage.py runserver 0.0.0.0:%s" % port)


@task(task_class=ConfigTask)
def ssh(ec2_instance=''):
    """
    Log into the EC2 instance using SSH.
    """
    if not ec2_instance:
        try:
            ec2_instance = env.hosts[0]
        except IndexError:
            ec2_instance = prompt('EC2 Host:')
    local("ssh %s@%s -i %s" % (env.user, ec2_instance, env.key_filename[0]))
