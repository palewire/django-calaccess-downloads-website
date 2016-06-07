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
    data = {
        "run_list": [
            "ccdc::default",
            "ccdc::python",
            "ccdc::apps",
            "ccdc::cron"
        ],
    
        "base_packages": [
            "git-core",
            "bash-completion"
        ],
    
        "users": {
            "ccdc": {
              "id": 1003,
              "full_name": "ccdc"
            }
        },
    
        "groups": {
            "ccdc": {
              "gid": 203,
              "members": ["ccdc"]
            }
        },
    
        "ubuntu_python_packages": [
            "python-setuptools",
            "python-pip",
            "python-dev",
            "libpq-dev",
            "python-virtualenv",
            "fabric"
        ],
    
        "pip_python_packages": {},
    
        "app": {
            "name": "calaccess",
            "repo": "https://github.com/california-civic-data-coalition/django-calaccess-downloads-website.git",
            "branch": "master"
        },

        "apps_user": "ccdc",
        "apps_group": "ccdc",
        "apps_password": "ccdc",

        "db_user_password": env.DB_USER_PASSWORD,
        "db_host": env.RDS_HOST,

        "aws_access_key_id": env.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": env.AWS_SECRET_ACCESS_KEY,

        "crons": {
            "update": {
                "minute": "2",
                "hour": "7",
                "command": "/apps/calaccess/bin/python /apps/calaccess/repo/manage.py updatecalaccessrawdata --noinput --skip-load"
            }
        }
    }

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
    sudo('cd /etc/chef && %s' % env.chef, pty=True)
