#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import collections
from app import migrate, collectstatic
from configure import ConfigTask, copyconfig
from fabric.api import sudo, task, env
from fabric.contrib.project import rsync_project
from fabric.colors import green


@task(task_class=ConfigTask)
def bootstrap():
    """
    Install Chef and use it to install the app on an EC2 instance.
    """
    # Prepare node to use secrets from our configuration file
    rendernodejson()

    # Install chef and run it
    installchef()
    cook()

    # Copy local env to new instance
    copyconfig()

    # Set the CALACCESS_WEBSITE_ENV var when the virtualenv is activated.
    # Otherwise the Django project will default to DEV.
    sudo("echo 'export CALACCESS_WEBSITE_ENV=%s' >> "
         "/apps/calaccess/bin/activate" % env.config_section)

    # Fire up the Django project
    migrate()
    collectstatic()

    # Done deal
    print(green("Success!"))
    print("Visit the app at %s" % env.EC2_HOST)


@task(task_class=ConfigTask)
def installchef(version='13.0.118'):
    """
    Install Chef, after updating apt-get.

    Defaults to version 13.0.118.
    """
    # Update apt-get
    sudo('apt-get update', pty=True)
    # Install Chef
    sudo(
        'curl -L https://www.chef.io/chef/install.sh | sudo bash -s -- -v %s' % version,
         pty=True,
    )


@task(task_class=ConfigTask)
def rendernodejson():
    """
    Render chef's node.json file from a template
    """
    template = open("./chef/node.json.template", "r").read()
    data = json.loads(
        template % env,
        object_pairs_hook=collections.OrderedDict
    )
    with open('./chef/node.json', 'w') as f:
        json.dump(data, f, indent=4, separators=(',', ': '))


@task(task_class=ConfigTask)
def cook():
    """
    Update Chef cookbook and execute it.
    """
    sudo('mkdir -p /etc/chef')
    sudo('chown ubuntu -R /etc/chef')
    rsync_project("/etc/chef/", "./chef/")
    sudo('cd /etc/chef && /usr/bin/chef-solo -c solo.rb -j node.json', pty=True)
