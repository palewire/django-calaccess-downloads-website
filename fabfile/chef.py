import collections
from configure import ConfigTask
from fabric.api import sudo, task, env
from fabric.contrib.project import rsync_project
import json


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
    template["db_user_password"] = env.DB_USER_PASSWORD
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
