from configure import ConfigTask
from fabric.api import sudo, task, env
from fabric.contrib.project import rsync_project


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
def cook():
    """
    Update Chef cookbook and execute it.
    """
    sudo('mkdir -p /etc/chef')
    sudo('chown ubuntu -R /etc/chef')
    rsync_project("/etc/chef/", "./chef/")
    sudo('cd /etc/chef && %s' % env.chef, pty=True)
