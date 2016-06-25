#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import collections
from app import migrate, collectstatic
from configure import ConfigTask, copy_config
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

    # source secrets in activate script
    sudo("echo 'source /apps/calaccess/.secrets' >> /apps/calaccess/bin/activate")

    # Copy local env to new instance
    copy_config()

    # Fire up the Django project
    migrate()
    collectstatic()

    # Done deal
    print(green("Success!"))
    print "Visit the app at %s" % env.EC2_HOST


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
    template = json.load(
        open("./chef/node.json.template", "r"),
        object_pairs_hook=collections.OrderedDict
    )
    template["db_password"] = env.DB_USER_PASSWORD
    template["db_host"] = env.RDS_HOST
    template["aws_access_key_id"] = env.AWS_ACCESS_KEY_ID
    template["aws_secret_access_key"] = env.AWS_SECRET_ACCESS_KEY
    template["crons"]["update"] = {
        "minute": "25",
        "hour": "5,11,17,23",
        "command": "source /apps/calaccess/bin/activate && /apps/calaccess/bin/"
                   "python {project_dir}manage.py updatecalaccessrawdata "
                   "--noinput --verbosity=3 2>&1 > output.log".format(**env)
    }

    with open('./chef/node.json', 'w') as f:
        json.dump(template, f, indent=4, separators=(',', ': '))


@task(task_class=ConfigTask)
def cook():
    """
    Update Chef cookbook and execute it.
    """
    sudo('mkdir -p /etc/chef')
    sudo('chown ubuntu -R /etc/chef')
    rsync_project("/etc/chef/", "./chef/")
    sudo('cd /etc/chef && %s' % env.chef, pty=True)
