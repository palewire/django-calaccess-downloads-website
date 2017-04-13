#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
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

    # Fire up the Django project
    migrate()
    collectstatic()

    sudo("echo 'export CALACCESS_WEBSITE_ENV=%s' >> "
         "/apps/calaccess/bin/activate" % env.config_section)

    # Done deal
    print(green("Success!"))
    print("Visit the app at %s" % env.EC2_HOST)


@task(task_class=ConfigTask)
def installchef():
    """
    Install all the dependencies to run a Chef cookbook
    """
    # Install dependencies
    sudo('apt-get update', pty=True)
    sudo('apt-get install -y git-core ruby2.0 ruby2.0-dev', pty=True)
    # Screw ruby docs.
    sudo("echo 'gem: --no-ri --no-rdoc' > /root/.gemrc")
    sudo("echo 'gem: --no-ri --no-rdoc' > /home/ubuntu/.gemrc")
    # Install Chef
    sudo('curl -L https://www.chef.io/chef/install.sh | sudo bash', pty=True)


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
